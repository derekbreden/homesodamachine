// Replays the five-part faucet plate against material deposited before each move.
// The terrain and head are sampled rasters. The native command timestamps below are feed-time estimates.
#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numbers>
#include <ranges>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
constexpr double pitch = 0.5;
constexpr double motion_sample = 0.5;
constexpr double arc_sample = 0.25;
constexpr int tile = 8;
constexpr double infinity = std::numeric_limits<double>::infinity();
constexpr double nominal_z_limit = 30.0;
constexpr double travel_tolerance = 0.31;
constexpr double bed_x = 325.0;
constexpr double bed_y = 320.0;
constexpr double bed_z = 325.0;
constexpr double tip_flat_r = 0.34;
constexpr double tip_cone_r = 2.0;
constexpr double tip_cone_height = 2.48;
constexpr double nearby_pitch = 0.10;
constexpr double tau = std::numbers::pi * 2.0;
constexpr double unfilled = -1000.0;

using Point = std::array<double, 3>;

bool removable_feature(std::string_view feature) {
    return feature.starts_with("Support") || feature == "Brim" || feature == "Skirt";
}

std::string_view trim(std::string_view text) {
    const auto start = text.find_first_not_of(" \t\r");
    if (start == std::string_view::npos) return {};
    return text.substr(start, text.find_last_not_of(" \t\r") - start + 1);
}

struct Words {
    std::array<double, 26> values{};
    std::array<bool, 26> seen{};

    explicit Words(std::string_view text) {
        const char *p = text.data();
        const char *end = p + text.size();
        while (p < end) {
            const char key = *p++;
            if (key < 'A' || key > 'Z') continue;
            const char *start = p;
            while (p < end && (*p == '-' || *p == '+' || *p == '.' || (*p >= '0' && *p <= '9'))) ++p;
            if (p != start) {
                seen[key - 'A'] = true;
                values[key - 'A'] = std::strtod(start, nullptr);
            }
        }
    }
    bool has(char key) const { return seen[key-'A']; }
    double get(char key, double fallback = 0) const {
        return has(key) ? values[key-'A'] : fallback;
    }
};

int floor_div(int value, int divisor) {
    int result = value / divisor;
    if (value < 0 && value % divisor != 0) --result;
    return result;
}

struct Cell {
    float height = 0.0f;
    float time = unfilled;
    int object = 0;
    bool removable = false;
};

struct Terrain {
    // The travel raster extends beyond the usable print plate for the nozzle and the head.
    static constexpr int x0 = -208;
    static constexpr int y0 = -208;
    static constexpr int width = 1280;
    static constexpr int height = 1280;
    static constexpr int tiles_x = width / tile;
    static constexpr int tiles_y = height / tile;

    std::vector<Cell> cells = std::vector<Cell>(width * height);
    std::vector<float> highest = std::vector<float>(tiles_x * tiles_y);
    std::vector<int> source = std::vector<int>(tiles_x * tiles_y);

    static int index_x(double mm) { return static_cast<int>(std::lround(mm / pitch)) - x0; }
    static int index_y(double mm) { return static_cast<int>(std::lround(mm / pitch)) - y0; }
    static double x_at(int i) { return (i + x0) * pitch; }
    static double y_at(int j) { return (j + y0) * pitch; }

    const Cell& get(int i, int j) const {
        static const Cell empty{};
        if (i < 0 || j < 0 || i >= width || j >= height) return empty;
        return cells[j * width + i];
    }
    double tile_max(int i, int j) const {
        if (i < 0 || j < 0 || i >= tiles_x || j >= tiles_y) return 0.0;
        return highest[j * tiles_x + i];
    }
    bool tile_may_have_other_object(int i, int j, int object) const {
        if (i < 0 || j < 0 || i >= tiles_x || j >= tiles_y) return false;
        const int producer = source[j * tiles_x + i];
        return producer != 0 && producer != object;
    }
    void add(int i, int j, float z, float time, int object, bool removable) {
        if (i < 0 || j < 0 || i >= width || j >= height) return;
        Cell &cell = cells[j * width + i];
        if (z < cell.height - 1.0e-5f) return;
        cell = {z, time, object, removable};
        const int index = (j / tile) * tiles_x + i / tile;
        auto &top = highest[index];
        top = std::max(top, z);
        auto &producer = source[index];
        if (producer == 0) producer = object;
        else if (object != 0 && producer != object) producer = -1;
    }
};

struct HeadCell {
    int x, y;
    double height;
};

struct Block {
    int dx = 0, dy = 0;
    double underside = infinity;
    std::vector<HeadCell> cells;
};

struct Clearance {
    double gap = infinity;
    Point xyz{};
    double time = 0.0;
    std::size_t line = 0;
    int object = 0;
    int obstacle = 0;
    int offset_x = 0, offset_y = 0;
    bool earlier_bead_removable = false;
};

struct Head {
    std::array<std::vector<Block>, tile * tile> body;
    std::vector<HeadCell> flank;
    double lowest_body = infinity;

    explicit Head(const std::string& map_path) {
        std::ifstream stream(map_path);
        if (!stream) throw std::runtime_error("cannot read the height map");
        char code;
        int x, y;
        double z;
        while (stream >> code >> x >> y >> z) {
            if (code == 'N') {
                if (std::hypot(x * pitch, y * pitch) >= 0.6) flank.push_back({x, y, z});
                continue;
            }
            lowest_body = std::min(lowest_body, z);
            for (int ry = 0; ry < tile; ++ry) {
                for (int rx = 0; rx < tile; ++rx) {
                    auto &row = body[ry * tile + rx];
                    const int dx = floor_div(x + rx, tile);
                    const int dy = floor_div(y + ry, tile);
                    auto found = std::ranges::find_if(row, [&](const Block& b) {
                        return b.dx == dx && b.dy == dy;
                    });
                    if (found == row.end()) {
                        row.push_back({dx, dy, z, {{x, y, z}}});
                    } else {
                        found->underside = std::min(found->underside, z);
                        found->cells.push_back({x, y, z});
                    }
                }
            }
        }
        // Low hardware offers a smaller bound and is visited first.
        for (auto &blocks : body) {
            std::ranges::sort(blocks, {}, &Block::underside);
        }
    }
};

struct LocalClearance {
    double gap = infinity;
    Point nozzle{}, bead{};
    double age = 0, radius = 0;
    std::size_t line = 0, source_line = 0;
    int object = 0, deposited_by = 0;
    std::string feature;
    bool earlier_bead_removable = false;
};

struct NozzleClearance {
    LocalClearance fresh_flat, adjacent_flat, adjacent_cone, travel_flat, travel_cone;
    LocalClearance earlier_support_flat, earlier_support_cone, earlier_part_flat, earlier_part_cone;
    LocalClearance dry_support_flat, dry_support_cone, dry_part_flat, dry_part_cone, dry_center;
    double total_road_mm = 0.0, downslope_road_mm = 0.0;
    double fresh_flat_past_005_road_mm = 0.0;
    double sampled_fresh_flat_past_005_road_mm = 0.0;
    double adjacent_past_01_road_mm = 0.0;
    double adjacent_past_02_road_mm = 0.0;
    double outer_wall_mm = 0.0, outer_wall_fresh_past_005_road_mm = 0.0;
    double outer_wall_sampled_fresh_past_005_road_mm = 0.0;
    double outer_wall_adjacent_past_01_road_mm = 0.0;
    std::size_t sampled = 0, travel_sampled = 0;
};

struct LocalSample {
    double fresh_flat = 0.0, adjacent = 0.0;
};

struct LocalPoint {
    float height = 0.0f, time = unfilled;
    int run = 0, object = 0;
    std::size_t line = 0;
    bool removable = false;
};

struct LocalTerrain {
    double x0, y0, x1, y1;
    int nx, ny;
    std::vector<LocalPoint> points;

    LocalTerrain(double min_x, double min_y, double max_x, double max_y)
        : x0(min_x), y0(min_y), x1(max_x), y1(max_y),
          nx(1 + static_cast<int>(std::lround((x1 - x0) / nearby_pitch))),
          ny(1 + static_cast<int>(std::lround((y1 - y0) / nearby_pitch))),
          points(static_cast<std::size_t>(nx) * ny) {}

    double x(int i) const { return x0 + i * nearby_pitch; }
    double y(int j) const { return y0 + j * nearby_pitch; }

    bool nearby(const Point& p) const {
        return p[0] > x0 - tip_cone_r && p[0] < x1 + tip_cone_r
            && p[1] > y0 - tip_cone_r && p[1] < y1 + tip_cone_r;
    }
    bool possibly_crosses(const Point& first, const Point& last, double pad = 0.0) const {
        const double extension = tip_cone_r + pad;
        return std::min(first[0], last[0]) < x1 + extension && std::max(first[0], last[0]) > x0 - extension
            && std::min(first[1], last[1]) < y1 + extension && std::max(first[1], last[1]) > y0 - extension;
    }
    void add(const Point& a, const Point& b, double width, double height, double time0,
             double time1, int run, int object, std::size_t line, bool removable) {
        const double dx = b[0]-a[0], dy = b[1]-a[1], length2 = dx*dx+dy*dy;
        if (length2 <= 1e-16 || width <= 0.0 || (!nearby(a) && !nearby(b))) return;
        const double r = width / 2.0;
        const double flat = std::max(0.0, (width - height) / 2.0);
        const double flank = r - flat;
        int i0 = std::max(0, static_cast<int>(std::ceil((std::min(a[0],b[0]) - r - x0) / nearby_pitch)));
        int i1 = std::min(nx - 1, static_cast<int>(std::floor((std::max(a[0],b[0]) + r - x0) / nearby_pitch)));
        int j0 = std::max(0, static_cast<int>(std::ceil((std::min(a[1],b[1]) - r - y0) / nearby_pitch)));
        int j1 = std::min(ny - 1, static_cast<int>(std::floor((std::max(a[1],b[1]) + r - y0) / nearby_pitch)));
        for (int j = j0; j <= j1; ++j) {
            for (int i = i0; i <= i1; ++i) {
                const double ux = x(i)-a[0], uy = y(j)-a[1];
                const double t = std::clamp((ux*dx+uy*dy)/length2, 0.0, 1.0);
                const double lateral2 = std::pow(ux-t*dx, 2) + std::pow(uy-t*dy, 2);
                if (lateral2 > r*r) continue;
                const double round_fraction = flank <= 1e-9 ? 0.0
                    : std::clamp((std::sqrt(lateral2)-flat) / flank, 0.0, 1.0);
                const double edge_drop = height / 2 * (1.0 - std::sqrt(1.0 - round_fraction * round_fraction));
                const double z = a[2]+(b[2]-a[2])*t-edge_drop;
                auto &last = points[j*nx+i];
                if (z >= last.height - 1e-5) {
                    last = {static_cast<float>(z), static_cast<float>(time0+(time1-time0)*t),
                            run, object, line, removable};
                }
            }
        }
    }
    LocalSample nozzle(const Point& p, double time, int run, int object, std::size_t line,
                       const std::string& feature, NozzleClearance& summary, bool laying) const {
        LocalSample sampled;
        if (!nearby(p)) return sampled;
        if (laying) ++summary.sampled; else ++summary.travel_sampled;
        int i0 = std::max(0, static_cast<int>(std::ceil((p[0]-tip_cone_r-x0)/nearby_pitch)));
        int i1 = std::min(nx - 1, static_cast<int>(std::floor((p[0]+tip_cone_r-x0)/nearby_pitch)));
        int j0 = std::max(0, static_cast<int>(std::ceil((p[1]-tip_cone_r-y0)/nearby_pitch)));
        int j1 = std::min(ny - 1, static_cast<int>(std::floor((p[1]+tip_cone_r-y0)/nearby_pitch)));
        for (int j = j0; j <= j1; ++j) {
            for (int i = i0; i <= i1; ++i) {
                const auto &last = points[j*nx+i];
                if (last.height <= p[2] && last.height < p[2] - 0.3) continue;
                const double ux = x(i)-p[0], uy = y(j)-p[1];
                const double r2 = ux*ux+uy*uy;
                if (r2 > tip_cone_r*tip_cone_r) continue;
                if (r2 < 0.20*0.20) {
                    const double gap = p[2]-last.height;
                    if (!laying && last.object != 0 && gap < summary.dry_center.gap)
                        summary.dry_center = {gap, p, {x(i), y(j), last.height}, time-last.time,
                            std::sqrt(r2), line, last.line, object, last.object, feature, last.removable};
                    continue;
                }
                const bool flat = r2 <= tip_flat_r*tip_flat_r;
                const bool same_run = last.run == run && last.object == object;
                const double radius = std::sqrt(r2);
                const double rise = flat ? 0.0 : tip_cone_height * (radius-tip_flat_r) / (tip_cone_r-tip_flat_r);
                const double gap = p[2] + rise - last.height;
                LocalClearance* result;
                LocalClearance* material = nullptr;
                if (!laying) {
                    result = flat ? &summary.travel_flat : &summary.travel_cone;
                    if (last.removable) material = flat ? &summary.dry_support_flat : &summary.dry_support_cone;
                    else material = flat ? &summary.dry_part_flat : &summary.dry_part_cone;
                }
                else if (same_run) {
                    if (!flat) continue;
                    sampled.fresh_flat = std::min(sampled.fresh_flat, gap);
                    result = &summary.fresh_flat;
                } else {
                    sampled.adjacent = std::min(sampled.adjacent, gap);
                    result = flat ? &summary.adjacent_flat : &summary.adjacent_cone;
                    if (last.removable) material = flat ? &summary.earlier_support_flat : &summary.earlier_support_cone;
                    else material = flat ? &summary.earlier_part_flat : &summary.earlier_part_cone;
                }
                if (gap < result->gap || (material && gap < material->gap)) {
                    const LocalClearance reading {gap, p, {x(i), y(j), last.height}, time-last.time,
                        radius, line, last.line, object, last.object, feature, last.removable};
                    if (gap < result->gap) *result = reading;
                    if (material && gap < material->gap) *material = reading;
                }
            }
        }
        return sampled;
    }
};

struct Activity {
    std::size_t moves = 0, samples = 0, travel_samples = 0;
    std::size_t travel_below_samples = 0, travel_below_moves = 0, unprimed_moves = 0;
    double seconds = 0, max_z_feed = 0, max_deposit_z_feed = 0, extrusion = 0;
    double max_retraction_debt_while_moving_extrusion = 0;
    Clearance body, flank, travel_body, travel_tip;
};

struct Object {
    double first = -1, first_model = -1, last = -1, last_model = -1;
    double max_model_gap = 0, max_gap = 0, extrusion = 0, first_layer_extrusion = 0;
    double last_z = 0, max_gap_z_before = 0, max_gap_z_after = 0;
    double max_gap_time_before = 0, max_gap_time_after = 0;
    double first_z = 0, first_model_z = 0, first_280_time = -1;
    double first_nozzle = 0, first_model_nozzle = 0;
    double first_fan = 0, first_model_fan = 0;
    double first_bed_temperature = 0;
    double extrusion_first_bed_course_max_nozzle = 0;
    double max_x = -infinity, max_y = -infinity, max_z = -infinity;
    double min_x = infinity, min_y = infinity, min_z = infinity;
    std::map<int, double> fan_extrusion;
};

struct Arc {
    double cx = 0, cy = 0, radius = 0, start = 0, sweep = 0;

    Arc(const Point& a, const Point& b, const Words& words, bool clockwise, bool absolute_center) {
        if (words.has('R')) {
            const double signed_radius = words.get('R');
            radius = std::abs(signed_radius);
            const double dx = b[0] - a[0], dy = b[1] - a[1];
            const double chord = std::hypot(dx, dy);
            if (chord <= 1e-9 || chord > 2.0 * radius + 0.002 || radius <= 1e-9) {
                throw std::runtime_error("invalid R arc");
            }
            const double side = (clockwise == (signed_radius >= 0.0)) ? -1.0 : 1.0;
            const double rise = std::sqrt(std::max(0.0, radius * radius - chord * chord / 4.0));
            cx = (a[0] + b[0]) / 2.0 - side * dy / chord * rise;
            cy = (a[1] + b[1]) / 2.0 + side * dx / chord * rise;
        } else {
            cx = absolute_center ? words.get('I', a[0]) : a[0] + words.get('I');
            cy = absolute_center ? words.get('J', a[1]) : a[1] + words.get('J');
        }
        radius = std::hypot(a[0] - cx, a[1] - cy);
        if (radius <= 1e-9) {
            throw std::runtime_error("invalid IJ arc");
        }
        start = std::atan2(a[1] - cy, a[0] - cx);
        const double turns = words.get('P', 1);
        if (turns < 1 || turns != std::floor(turns)) throw std::runtime_error("invalid arc turns");
        if (std::hypot(a[0] - b[0], a[1] - b[1]) < 1e-8) {
            sweep = (clockwise ? -tau : tau) * turns;
        } else {
            const double end = std::atan2(b[1] - cy, b[0] - cx);
            sweep = std::fmod(clockwise ? start - end : end - start, tau);
            if (sweep <= 1e-9) sweep += tau;
            sweep = (clockwise ? -1 : 1) * (sweep + (turns - 1.0) * tau);
        }
    }
    Point at(const Point& a, const Point& b, double fraction) const {
        if (fraction >= 1) return b;
        const double angle = start + sweep * fraction;
        return {cx + radius * std::cos(angle), cy + radius * std::sin(angle),
                a[2] + fraction * (b[2] - a[2])};
    }
};

struct Replay {
    Head head;
    Terrain terrain;
    std::vector<LocalTerrain> local;
    std::map<std::string, NozzleClearance> local_by_phase;
    NozzleClearance* near_active = &local_by_phase["native"];
    std::string local_phase = "native";
    std::map<std::string, Activity> phase_stats;
    std::map<int, Object> objects;
    std::map<std::string, std::size_t> opaque_commands;
    std::string phase = "native";
    Activity *active = &phase_stats[phase];
    std::string feature;
    std::string native_tip_phase;
    double native_tip_low = 0.0, native_tip_high = 0.0, native_z = 0.0;
    Point current{0.0, 0.0, 0.0}, offset{};
    double e = 0.0, debt = 0.0, feed = 0.0, rate_multiplier = 1.0, flow_multiplier = 1.0;
    double time = 0.0, fan = 0.0, nozzle = 0.0, bed_temperature = 0.0, width = 0.42;
    double z_limit = nominal_z_limit, x_limit = 1000.0, y_limit = 1000.0, e_limit = 50.0;
    double largest_relative_obstacle = 0.0, fixed_wait = 0.0;
    bool absolute = true, absolute_e = false, absolute_center = false, xy_plane = true;
    bool recording = false, ended = false, prior_is_laying = false;
    int run = 0;
    std::size_t line = 0, arcs = 0, spiral_arcs = 0, unknown_deposit = 0;
    int object = 0;
    Clearance high_relative{};
    std::vector<Clearance> travel_violations;
    Clearance cross_object_witness{};
    std::map<int, std::array<double, 6>> first_three_by_object;

    explicit Replay(const std::string& map_file, std::vector<std::array<double, 4>> windows)
        : head(map_file) {
        for (const auto& limits : windows) local.emplace_back(limits[0], limits[1], limits[2], limits[3]);
        high_relative.gap = -infinity;
    }

    void witness(Clearance& best, double gap, const Point& p, double sample_time,
                 const Cell& obstacle, int dx, int dy) {
        if (gap < best.gap) best = {gap, p, sample_time, line, object, obstacle.object, dx, dy,
                                   obstacle.removable};
    }

    bool sample(const Point& p, bool laying, double sample_time) {
        Activity &result = *active;
        ++result.samples;
        const int i = Terrain::index_x(p[0]);
        const int j = Terrain::index_y(p[1]);
        const Cell &below = terrain.get(i, j);
        if (!laying) {
            ++result.travel_samples;
            witness(result.travel_tip, p[2] - below.height, p, sample_time, below, 0, 0);
            if (below.height > 0 && p[2] < below.height - travel_tolerance &&
                travel_violations.size() < 120) {
                Clearance occurrence;
                witness(occurrence, p[2] - below.height, p, sample_time, below, 0, 0);
                travel_violations.push_back(occurrence);
            }
        }
        const int ti = floor_div(i, tile), tj = floor_div(j, tile);
        const auto &blocks = head.body[(j - tj * tile) * tile + i - ti * tile];
        for (const Block& block: blocks) {
            const int block_x = ti + block.dx, block_y = tj + block.dy;
            const double peak = terrain.tile_max(block_x, block_y);
            const double possible = p[2] + block.underside - peak;
            const double below_nozzle = peak - p[2];
            if (below_nozzle > largest_relative_obstacle) {
                // A tile maximum is only a cheap upper bound. Confirm its nearest modeled cell.
                double verified = largest_relative_obstacle;
                for (const HeadCell& item: block.cells) {
                    const auto &floor = terrain.get(i + item.x, j + item.y);
                    const double delta = floor.height - p[2];
                    if (delta > verified) {
                        verified = delta;
                        high_relative = {delta, p, sample_time, line, object, floor.object,
                                         item.x, item.y, floor.removable};
                    }
                }
                largest_relative_obstacle = verified;
            }
            const double threshold = laying ? result.body.gap
                : std::max(result.body.gap, result.travel_body.gap);
            const bool compare_other = laying && object != 0 && possible < cross_object_witness.gap
                && terrain.tile_may_have_other_object(block_x, block_y, object);
            if (possible >= threshold && !compare_other) continue;
            for (const HeadCell& item: block.cells) {
                const Cell &floor = terrain.get(i + item.x, j + item.y);
                const double gap = p[2] + item.height - float(floor.height);
                witness(result.body, gap, p, sample_time, floor, item.x, item.y);
                if (!laying) witness(result.travel_body, gap, p, sample_time, floor, item.x, item.y);
                if (compare_other && floor.object != 0 && floor.object != object)
                    witness(cross_object_witness, gap, p, sample_time, floor, item.x, item.y);
            }
        }
        for (const HeadCell& item: head.flank) {
            const Cell &floor = terrain.get(i + item.x, j + item.y);
            const double gap = p[2] + item.height - float(floor.height);
            witness(result.flank, gap, p, sample_time, floor, item.x, item.y);
        }

        const bool bad_travel = !laying && below.height > 0 && p[2] < below.height - travel_tolerance;
        if (bad_travel) ++result.travel_below_samples;
        return bad_travel;
    }

    void deposit(const Point& from, const Point& to, double print_width, double start, double end) {
        // Stamp the swept nominal bead footprint. The nearest cell-center fallback retains thin beads.
        const double radius = print_width / 2.0;
        const bool disposable = removable_feature(feature);
        const double dx = to[0] - from[0], dy = to[1] - from[1];
        const double denominator = dx * dx + dy * dy;
        if (denominator <= 1e-16) return;
        const double max_x = std::max(from[0], to[0]) + radius;
        const double min_x = std::min(from[0], to[0]) - radius;
        const double max_y = std::max(from[1], to[1]) + radius;
        const double min_y = std::min(from[1], to[1]) - radius;
        for (int j = Terrain::index_y(min_y); j <= Terrain::index_y(max_y); ++j) {
            for (int i = Terrain::index_x(min_x); i <= Terrain::index_x(max_x); ++i) {
                const double rx = Terrain::x_at(i) - from[0], ry = Terrain::y_at(j) - from[1];
                const double factor = std::clamp((rx * dx + ry * dy) / denominator, 0.0, 1.0);
                if (std::hypot(rx - dx * factor, ry - dy * factor) <= radius) {
                    const double z = from[2] + (to[2] - from[2]) * factor;
                    terrain.add(i, j, z, start + (end - start) * factor, object, disposable);
                }
            }
        }
        // Match the old centerline check even when a road is narrower than the grid.
        auto core = [&](const Point& p, double t) {
            terrain.add(Terrain::index_x(p[0]), Terrain::index_y(p[1]), p[2], t, object, disposable);
        };
        core(from, start);
        core(to, end);
    }

    void stat_extrusion(const Point& from, const Point& to, double amount) {
        const bool solid = !removable_feature(feature);
        if (object == 0) ++unknown_deposit;
        Object &row = objects[object];
        if (row.first < 0.0) {
            row.first = time;
            row.first_z = to[2];
            row.first_nozzle = nozzle;
            row.first_bed_temperature = bed_temperature;
            row.first_fan = fan;
        } else if (time - row.last > row.max_gap) {
            row.max_gap = time - row.last;
            row.max_gap_time_before = row.last;
            row.max_gap_time_after = time;
            row.max_gap_z_before = row.last_z;
            row.max_gap_z_after = to[2];
        }
        row.last = time;
        row.last_z = to[2];
        if (solid) {
            if (row.first_model < 0.0) {
                row.first_model = time;
                row.first_model_z = to[2];
                row.first_model_nozzle = nozzle;
                row.first_model_fan = fan;
            } else {
                row.max_model_gap = std::max(row.max_model_gap, time - row.last_model);
            }
            row.last_model = time;
        }
        if (row.first_280_time < 0.0 && nozzle >= 278.0) row.first_280_time = time;
        row.extrusion += amount;
        row.fan_extrusion[std::lround(fan)] += amount;
        const double bead_top = std::max(from[2], to[2]);
        if (bead_top <= 0.205) {
            row.first_layer_extrusion += amount;
            row.extrusion_first_bed_course_max_nozzle = std::max(nozzle, row.extrusion_first_bed_course_max_nozzle);
        }
        if (object > 0 && object != 1901 && bead_top <= 0.685) {
            const int course = bead_top <= 0.205 ? 0 : bead_top <= 0.445 ? 1 : 2;
            auto &reported = first_three_by_object[object];
            reported[2 * course] += amount;
            if (nozzle > 270.0) reported[2 * course + 1] += amount;
        }
        row.min_x = std::min(row.min_x, std::min(from[0], to[0]) - width / 2.0);
        row.max_x = std::max(row.max_x, std::max(from[0], to[0]) + width / 2.0);
        row.min_y = std::min(row.min_y, std::min(from[1], to[1]) - width / 2.0);
        row.max_y = std::max(row.max_y, std::max(from[1], to[1]) + width / 2.0);
        row.min_z = std::min(row.min_z, std::min(from[2], to[2]));
        row.max_z = std::max(row.max_z, std::max(from[2], to[2]));
    }

    void set_phase(std::string_view name) {
        phase = name.empty() ? "native" : std::string(name);
        active = &phase_stats[phase];
        local_phase = phase;
        near_active = &local_by_phase[local_phase];
    }

    void classify_local(std::string_view stage) {
        local_phase = std::string(stage);
        near_active = &local_by_phase[local_phase];
    }

    void comment(std::string_view type) {
        if (type == "MACHINE_START_GCODE_END") {
            recording = true;
            debt = 0.0;
            return;
        }
        if (type == "MACHINE_END_GCODE_START") {
            ended = true;
            return;
        }
        if (!recording) return;
        auto starts = [&](std::string_view key) { return type.starts_with(key); };
        auto parse = [&](std::string_view key) { return std::strtod(type.data() + key.size(), nullptr); };
        if (starts("FEATURE:")) feature = trim(type.substr(8));
        else if (starts("LINE_WIDTH:")) width = parse("LINE_WIDTH:");
        else if (starts("Z_HEIGHT:")) native_z = parse("Z_HEIGHT:");
        else if (starts("OBJECT_ID:")) {
            // OBJECT_ID sometimes anticipates a later start. The explicit start/stop label governs.
            // Whole-base study tapes carry that object identifier only.
            if (local_phase == "donated tilted base") object = std::lround(parse("OBJECT_ID:"));
        } else if (starts("start printing object, unique label id:")) {
            object = std::lround(parse("start printing object, unique label id:"));
            if (!native_tip_phase.empty() && object == 1902 && native_z >= native_tip_low && native_z < native_tip_high)
                set_phase(native_tip_phase);
        } else if (starts("stop printing object")) {
            object = 0;
            if (!native_tip_phase.empty() && phase == native_tip_phase) set_phase("native");
        }
        else if (starts("===== sloped underside")) {
            set_phase("sloped underside");
            object = 1901;
        } else if (starts("===== end of the sloped underside")) {
            set_phase("native");
            object = 0;
        } else if (starts("HSM_PHASE:")) set_phase(trim(type.substr(10)));
        else if (starts("HSM_PHASE_TRAVEL:")) {
            const auto name = trim(type.substr(17));
            set_phase(name == "final clearance lift" ? name : "transfers between course groups");
        } else if (starts("HSM_DONOR_PHASE:")) set_phase(trim(type.substr(16)));
        else if (starts("HSM_BRIDGE_STITCH:")) set_phase(trim(type.substr(18)));
        else if (starts("HSM_TIP_PHASE:")) set_phase(trim(type.substr(14)));
    }

    void command(std::string_view text) {
        const auto stop = text.find_first_of(" \t");
        const std::string_view op = text.substr(0, stop);
        const Words words(stop == std::string_view::npos ? std::string_view{} : text.substr(stop));
        if (op == "G90") absolute = true;
        else if (op == "G91") absolute = false;
        else if (op == "G90.1") absolute_center = true;
        else if (op == "G91.1") absolute_center = false;
        else if (op == "M82") absolute_e = true;
        else if (op == "M83") absolute_e = false;
        else if (op == "G17") xy_plane = true;
        else if (op == "G18" || op == "G19") xy_plane = false;
        else if (op == "G92") {
            for (std::size_t axis = 0; axis < 3; ++axis) {
                const char key = "XYZ"[axis];
                if (words.has(key)) offset[axis] = current[axis] - words.get(key);
            }
            if (words.has('E')) e = words.get('E');
        } else if (op == "M203") {
            x_limit = words.get('X', x_limit); y_limit = words.get('Y', y_limit);
            z_limit = words.get('Z', z_limit); e_limit = words.get('E', e_limit);
        } else if (op == "M220") rate_multiplier = words.get('S', 100) / 100;
        else if (op == "M221") {
            if (words.has('S')) flow_multiplier = words.get('S') / 100;
        } else if (op == "M106" && words.get('P', 1) == 1) fan = words.get('S', 255);
        else if (op == "M107" && words.get('P', 1) == 1) fan = 0;
        else if (op == "M140" || op == "M190") {
            bed_temperature = words.get('S', words.get('R', bed_temperature));
            if (recording && op == "M190") ++opaque_commands[std::string(op)];
        }
        else if (op == "M104" || op == "M109") {
            nozzle = words.get('S', words.get('R', nozzle));
            if (recording && op == "M109") ++opaque_commands[std::string(op)];
        } else if (op == "G4") {
            if (!recording) return;
            const double dwell = words.get('P') / 1000.0 + words.get('S');
            fixed_wait += dwell;
            time += dwell;
            active->seconds += dwell;
        } else if (op == "G0" || op == "G1" || op == "G2" || op == "G3") {
            move(op, words);
        } else if (recording && (op.starts_with("T") || op == "G20" || op == "G5" ||
                   op == "G10" || op == "G11" || op.starts_with("G28") ||
                   op.starts_with("G29") || op.starts_with("G387") || op == "M400")) {
            ++opaque_commands[std::string(op)];
        }
    }

    void move(std::string_view op, const Words& words) {
        if (words.has('F')) feed = words.get('F') / 60.0;
        Point to = current;
        for (std::size_t axis = 0; axis < 3; ++axis) {
            const char key = "XYZ"[axis];
            if (words.has(key)) {
                to[axis] = absolute ? words.get(key) + offset[axis] : current[axis] + words.get(key);
            }
        }
        const double de = words.has('E') ? (absolute_e ? words.get('E') - e : words.get('E')) : 0.0;
        if (words.has('E')) e = absolute_e ? words.get('E') : e + de;
        const Point from = current;
        current = to;
        if (!recording) return;
        const double dz = to[2] - from[2], dx = to[0] - from[0], dy = to[1] - from[1];
        const bool arc = op == "G2" || op == "G3";
        if (arc && !xy_plane) throw std::runtime_error("non-XY arc");
        const Arc curve = arc ? Arc(from, to, words, op == "G2", absolute_center)
            : Arc({0, 0, 0}, {0, 0, 0}, Words("I1"), false, false);
        const double dxy = arc ? curve.radius * std::abs(curve.sweep) : std::hypot(dx, dy);
        const double length = std::hypot(dxy, dz);
        if (length <= 1e-9 && std::abs(de) <= 1e-9) return;
        if (feed <= 0.0 || rate_multiplier <= 0.0) {
            throw std::runtime_error("motion or extrusion has no positive feed");
        }
        if (arc) {
            ++arcs;
            if (std::hypot(dx, dy) < 1e-8 && std::abs(dz) > 1e-9) ++spiral_arcs;
        }
        const bool positive_e = de > 1e-9;
        const double needed = positive_e ? std::min(debt, de) : 0.0;
        const double printed = positive_e ? (de - needed) * flow_multiplier : 0.0;
        debt = std::max(0.0, debt - de);
        if (de > 0.0 && dxy > 1e-8 && needed > 0.01) {
            ++active->unprimed_moves;
            active->max_retraction_debt_while_moving_extrusion =
                std::max(active->max_retraction_debt_while_moving_extrusion, needed);
        }
        const bool laying = positive_e && dxy > 1e-8 && printed > 1e-9;
        if (laying && !prior_is_laying) ++run;
        prior_is_laying = laying;
        const double capped_feed = feed * rate_multiplier;
        const double axis_seconds = std::max({std::abs(dx) / x_limit, std::abs(dy) / y_limit,
                                              std::abs(dz) / z_limit, std::abs(de) / e_limit});
        const double seconds = std::max(axis_seconds,
            (length > 1e-9 ? length : std::abs(de)) / capped_feed);
        ++active->moves;
        active->seconds += seconds;
        const double z_rate = length > 1e-9 ? std::abs(dz) / length * capped_feed : 0.0;
        active->max_z_feed = std::max(active->max_z_feed, z_rate);
        if (laying) {
            active->max_deposit_z_feed = std::max(active->max_deposit_z_feed, z_rate);
            active->extrusion += printed;
        }
        if (length > 1e-9) {
            const bool near_motion = std::ranges::any_of(local, [&](const LocalTerrain& zone) {
                return zone.possibly_crosses(from, to, arc ? 2.0 * curve.radius : 0.0);
            });
            const int samples = std::max(1, int(std::ceil(length /
                (near_motion ? nearby_pitch : arc ? arc_sample : motion_sample))));
            const double raw_section = printed * (std::numbers::pi * 1.75 * 1.75 / 4) / length;
            const double nominal_section = raw_section / (0.9555 * (feature == "Bridge" ? 1.25 : 1.0));
            const double factor = 1.0 - std::numbers::pi / 4.0;
            const double disc = std::max(0.0, width*width - 4 * factor * nominal_section);
            const double local_height = std::clamp(
                (width - std::sqrt(disc)) / (2 * factor), 0.0, std::max(0.0, width));
            const double horizontal_length = dxy / samples;
            const bool compare_fresh_flat = near_motion && laying && dz < -0.01 && local_height > 0.0;
            const bool disposable = removable_feature(feature);
            if (near_motion && laying) {
                const bool outer_wall = feature == "Outer wall";
                near_active->total_road_mm += dxy;
                if (outer_wall) near_active->outer_wall_mm += dxy;
                if (dz < -1e-6) near_active->downslope_road_mm += dxy;
                // The straight, continuously laid road behind the tip spans the annulus.
                if (compare_fresh_flat && std::abs(dz)/dxy*tip_flat_r > 0.05) {
                    near_active->fresh_flat_past_005_road_mm += dxy;
                    if (outer_wall) near_active->outer_wall_fresh_past_005_road_mm += dxy;
                }
            }
            Point a = from;
            bool travel = false;
            const double delay = positive_e ? needed / de : 0.0;
            for (int segment = 1; segment <= samples; ++segment) {
                const double fraction = double(segment) / samples;
                Point p;
                if (arc) p = curve.at(from, to, fraction);
                else {
                    for (std::size_t axis = 0; axis < 3; ++axis) {
                        p[axis] = from[axis] + (to[axis] - from[axis]) * fraction;
                    }
                }
                const double at = time + fraction * seconds;
                const bool depositing = laying && fraction > delay;
                travel |= sample(p, depositing, at);
                if (near_motion) {
                    LocalSample point;
                    for (const auto& zone : local) {
                        if (zone.nearby(p)) {
                            const LocalSample one = zone.nozzle(p, at, run, object, line, feature,
                                                                *near_active, depositing);
                            point.fresh_flat = std::min(point.fresh_flat, one.fresh_flat);
                            point.adjacent = std::min(point.adjacent, one.adjacent);
                        }
                    }
                    if (depositing) {
                        const bool outer_wall = feature == "Outer wall";
                        if (point.fresh_flat < -0.05) {
                            near_active->sampled_fresh_flat_past_005_road_mm += horizontal_length;
                            if (outer_wall) near_active->outer_wall_sampled_fresh_past_005_road_mm += horizontal_length;
                        }
                        if (point.adjacent < -0.1) {
                            near_active->adjacent_past_01_road_mm += horizontal_length;
                            if (outer_wall) near_active->outer_wall_adjacent_past_01_road_mm += horizontal_length;
                        }
                        if (point.adjacent < -0.2) near_active->adjacent_past_02_road_mm += horizontal_length;
                    }
                }
                if (depositing) {
                    if (segment == 1 && delay > 0.0) {
                        for (std::size_t axis = 0; axis < 3; ++axis) a[axis] =
                            from[axis] + (to[axis] - from[axis]) * delay;
                    }
                    const double start = time + (fraction - 1.0 / samples) * seconds;
                    deposit(a, p, width, start, at);
                    if (near_motion) {
                        for (auto& zone : local) {
                            if (zone.nearby(p) || zone.nearby(a))
                                zone.add(a, p, width, local_height, start, at, run, object, line, disposable);
                        }
                    }
                    stat_extrusion(a, p, printed / samples);
                }
                a = p;
            }
            if (travel) ++active->travel_below_moves;
        }
        time += seconds;
    }

    void read(std::istream& stream) {
        std::string raw;
        while (std::getline(stream, raw)) {
            ++line;
            std::string_view text = trim(raw);
            try {
                if (text.starts_with(';')) comment(trim(text.substr(1)));
                else if (!text.empty()) command(trim(text.substr(0, text.find(';'))));
            } catch (const std::exception& err) {
                throw std::runtime_error("line " + std::to_string(line) + ": " + err.what());
            }
            if (ended) break;
        }
        if (!ended || !recording) throw std::runtime_error("machine-start or machine-end boundaries absent");
    }
};

void quote(std::ostream& os, std::string_view value) {
    os << '"';
    for (char c: value) {
        if (c == '"' || c == '\\') os << '\\';
        if (c == '\t') os << "\\t";
        else if (c == '\n') os << "\\n";
        else if (c == '\r') os << "\\r";
        else os << c;
    }
    os << '"';
}

void output(std::ostream& os, const LocalClearance& found) {
    if (!std::isfinite(found.gap)) { os << "null"; return; }
    os << "{\"gap_mm\": " << found.gap << ", \"line\": " << found.line
       << ", \"from_line\": " << found.source_line
       << ", \"nozzle_xyz_mm\": [" << found.nozzle[0] << ", " << found.nozzle[1] << ", " << found.nozzle[2]
       << "], \"deposited_xyz_mm\": [" << found.bead[0] << ", " << found.bead[1] << ", " << found.bead[2]
       << "], \"deposited_age_s_at_nominal_feed\": " << found.age
       << ", \"distance_from_tip_center_mm\": " << found.radius
       << ", \"object\": " << found.object << ", \"deposited_by\": " << found.deposited_by
       << ", \"feature\": ";
    quote(os, found.feature);
    if (found.source_line > 0) os << ", \"deposited_material\": \""
       << (found.earlier_bead_removable ? "support" : "part") << '"';
    os << '}';
}

void output(std::ostream& os, const Clearance& found) {
    if (!std::isfinite(found.gap)) { os << "null"; return; }
    os << "{\"gap_mm\": " << found.gap << ", \"line\": " << found.line
       << ", \"xyz_mm\": [" << found.xyz[0] << ", " << found.xyz[1] << ", " << found.xyz[2]
       << "], \"head_cell_offset_xy_mm\": [" << found.offset_x * pitch << ", " << found.offset_y * pitch
       << "], \"object\": " << found.object << ", \"deposited_by\": " << found.obstacle
       << ", \"minimum_elapsed_s\": " << found.time;
    if (found.obstacle > 0) os << ", \"deposited_material\": \""
       << (found.earlier_bead_removable ? "support" : "part") << '"';
    os << '}';
}

void output(std::ostream& os, const Replay& replay) {
    os << std::fixed << std::setprecision(5);
    os << "{\n  \"grid_mm\": " << pitch << ",\n  \"motion_sample_mm\": " << motion_sample
       << ",\n  \"arc_step_mm\": " << arc_sample
       << ",\n  \"arc_count\": " << replay.arcs
       << ",\n  \"full_turn_lifts\": " << replay.spiral_arcs
       << ",\n  \"declared_dwell_s\": " << replay.fixed_wait
       << ",\n  \"minimum_feed_time_s\": " << replay.time
       << ",\n  \"unknown_extrusion_samples\": " << replay.unknown_deposit
       << ",\n  \"unexpanded_machine_commands\": {";
    bool comma = false;
    for (const auto& [key, count]: replay.opaque_commands) {
        if (comma) os << ", ";
        quote(os, key); os << ": " << count;
        comma = true;
    }
    os << "},\n  \"largest_prior_terrain_height_above_active_tip_mm\": " << replay.largest_relative_obstacle
       << ",\n  \"largest_prior_terrain_witness\": ";
    output(os, replay.high_relative);
    os << ",\n  \"modeled_cross_object_clearance_witness_while_depositing\": ";
    output(os, replay.cross_object_witness);
    os << ",\n  \"first_three_companion_courses_by_extrusion_temperature\": {";
    comma = false;
    for (const auto& [id, report]: replay.first_three_by_object) {
        if (comma) os << ", ";
        os << '"' << id << "\": [";
        for (int course = 0; course < 3; ++course) {
            if (course > 0) os << ", ";
            os << "{\"net_filament_mm\": " << report[2*course]
               << ", \"net_at_nozzle_setpoint_over_270_c_mm\": " << report[2*course+1] << "}";
        }
        os << "]";
        comma = true;
    }
    os << "},\n  \"phases\": {";
    comma = false;
    for (const auto& [key, stats]: replay.phase_stats) {
        if (comma) os << ',';
        os << "\n    "; quote(os, key);
        os << ": {\n      \"moves\": " << stats.moves << ", \"samples\": " << stats.samples
           << ", \"travel_samples\": " << stats.travel_samples
           << ", \"minimum_feed_time_s\": " << stats.seconds
           << ", \"extrusion_mm\": " << stats.extrusion
           << ",\n      \"minimum_head_body\": ";
        output(os, stats.body);
        os << ",\n      \"minimum_travel_head_body\": ";
        output(os, stats.travel_body);
        os << ",\n      \"minimum_nozzle_flank\": ";
        output(os, stats.flank);
        os << ",\n      \"minimum_travel_tip\": ";
        output(os, stats.travel_tip);
        os << ",\n      \"travel_samples_below_prior_bead_by_over_0_31_mm\": " << stats.travel_below_samples
           << ", \"affected_moves\": " << stats.travel_below_moves
           << ",\n      \"extrusion_travelling_with_retraction_debt\": " << stats.unprimed_moves
           << ", \"maximum_retraction_mismatch_mm\": " << stats.max_retraction_debt_while_moving_extrusion
           << ",\n      \"max_commanded_z_mm_per_s\": " << stats.max_z_feed
           << ", \"max_commanded_extruding_z_mm_per_s\": " << stats.max_deposit_z_feed << "\n    }";
        comma = true;
    }
    os << "\n  },\n  \"local_nozzle_model\": {";
    comma = false;
    for (const auto& [key, contact]: replay.local_by_phase) {
        if (contact.sampled == 0 && contact.travel_sampled == 0) continue;
        if (comma) os << ',';
        os << "\n    "; quote(os, key);
        os << ": {\n      \"extrusion_samples\": " << contact.sampled
           << ", \"travel_samples\": " << contact.travel_sampled
           << ", \"tested_road_mm\": " << contact.total_road_mm
           << ", \"downhill_road_mm\": " << contact.downslope_road_mm
           << ", \"outer_wall_road_mm\": " << contact.outer_wall_mm
           << ", \"outer_wall_straight_descent_flat_relief_demand_over_0_05_mm_road_mm\": "
           << contact.outer_wall_fresh_past_005_road_mm
           << ", \"straight_descent_flat_relief_demand_over_0_05_mm_road_mm\": " << contact.fresh_flat_past_005_road_mm
           << ",\n      \"road_mm_sampled_fresh_flat_gap_below_minus_0_05\": " << contact.sampled_fresh_flat_past_005_road_mm
           << ", \"outer_wall_road_mm_sampled_fresh_flat_gap_below_minus_0_05\": "
           << contact.outer_wall_sampled_fresh_past_005_road_mm
           << ", \"outer_wall_road_mm_adjacent_model_gap_below_minus_0_1\": " << contact.outer_wall_adjacent_past_01_road_mm
           << ",\n      \"road_mm_adjacent_model_gap_below_minus_0_1\": " << contact.adjacent_past_01_road_mm
           << ", \"road_mm_adjacent_model_gap_below_minus_0_2\": " << contact.adjacent_past_02_road_mm
           << ",\n      \"fresh_same_run_flat\": "; output(os, contact.fresh_flat);
        os << ",\n      \"prior_road_flat_during_extrusion\": "; output(os, contact.adjacent_flat);
        os << ",\n      \"prior_road_cone_during_extrusion\": "; output(os, contact.adjacent_cone);
        os << ",\n      \"prior_support_flat_during_extrusion\": "; output(os, contact.earlier_support_flat);
        os << ",\n      \"prior_support_cone_during_extrusion\": "; output(os, contact.earlier_support_cone);
        os << ",\n      \"prior_part_flat_during_extrusion\": "; output(os, contact.earlier_part_flat);
        os << ",\n      \"prior_part_cone_during_extrusion\": "; output(os, contact.earlier_part_cone);
        os << ",\n      \"dry_travel_flat\": "; output(os, contact.travel_flat);
        os << ",\n      \"dry_travel_cone\": "; output(os, contact.travel_cone);
        os << ",\n      \"dry_travel_flat_against_support\": "; output(os, contact.dry_support_flat);
        os << ",\n      \"dry_travel_cone_against_support\": "; output(os, contact.dry_support_cone);
        os << ",\n      \"dry_travel_flat_against_part\": "; output(os, contact.dry_part_flat);
        os << ",\n      \"dry_travel_cone_against_part\": "; output(os, contact.dry_part_cone);
        os << ",\n      \"dry_travel_occupied_nominal_center\": "; output(os, contact.dry_center);
        os << "\n    }";
        comma = true;
    }
    os << "\n  },\n  \"objects\": {";
    comma = false;
    double min_x = infinity, min_y = infinity, min_z = infinity;
    double max_x = -infinity, max_y = -infinity, max_z = -infinity;
    for (const auto& [id, row]: replay.objects) {
        if (comma) os << ',';
        os << "\n    \"" << id << "\": {"
           << "\"first_extrusion_s\": " << row.first << ", \"first_model_s\": " << row.first_model
           << ", \"first_extrusion_z_mm\": " << row.first_z << ", \"first_model_z_mm\": " << row.first_model_z
           << ", \"first_extrusion_commanded_nozzle_c\": " << row.first_nozzle
           << ", \"first_extrusion_commanded_bed_c\": " << row.first_bed_temperature
           << ", \"first_model_commanded_nozzle_c\": " << row.first_model_nozzle
           << ", \"first_model_commanded_fan_pwm\": " << row.first_model_fan
           << ", \"first_extrusion_commanded_fan_pwm\": " << row.first_fan
           << ", \"first_extrusion_at_regular_nozzle_temp_s\": " << row.first_280_time
           << ", \"max_model_idle_s\": " << row.max_model_gap
           << ", \"max_extrusion_idle_s\": " << row.max_gap
           << ", \"max_extrusion_idle_between_z_mm\": [" << row.max_gap_z_before << ", " << row.max_gap_z_after << "]"
           << ", \"max_extrusion_idle_at_s\": [" << row.max_gap_time_before << ", " << row.max_gap_time_after << "]"
           << ", \"extrusion_mm\": " << row.extrusion
           << ", \"first_bed_course_extrusion_mm\": " << row.first_layer_extrusion
           << ", \"first_bed_course_max_commanded_nozzle_c\": " << row.extrusion_first_bed_course_max_nozzle
           << ", \"bead_bounds_mm\": [[" << row.min_x << ", " << row.min_y << ", " << row.min_z
           << "], [" << row.max_x << ", " << row.max_y << ", " << row.max_z
           << "]], \"extrusion_mm_by_commanded_fan_pwm\": {";
        bool separate = false;
        for (const auto& [pwm, amount]: row.fan_extrusion) {
            if (separate) os << ", ";
            os << '"' << pwm << "\": " << amount;
            separate = true;
        }
        os << "}}";
        min_x = std::min(min_x, row.min_x); max_x = std::max(max_x, row.max_x);
        min_y = std::min(min_y, row.min_y); max_y = std::max(max_y, row.max_y);
        min_z = std::min(min_z, row.min_z); max_z = std::max(max_z, row.max_z);
        comma = true;
    }
    os << "\n  },\n  \"extrusion_bounds_mm\": [[" << min_x << ", " << min_y << ", " << min_z
       << "], [" << max_x << ", " << max_y << ", " << max_z << "]],"
       << "\n  \"minimum_shared_bed_edge_inset_mm\": " << std::min({min_x, min_y, bed_x - max_x, bed_y - max_y})
       << ",\n  \"height_available_above_deposited_mm\": " << bed_z - max_z
       << ",\n  \"initial_travel_anomalies\": [";
    comma = false;
    for (const Clearance& anomaly: replay.travel_violations) {
        if (comma) os << ", ";
        os << "\n    "; output(os, anomaly);
        comma = true;
    }
    os << "\n  ]\n}\n";
}
} // namespace

int main(int argc, char **argv) {
    try {
        if (argc < 3) throw std::runtime_error("usage: replay gcode headmap.txt [--base-nozzle] [--nozzle-box minX minY maxX maxY]...");
        std::vector<std::array<double, 4>> windows;
        std::array<double, 2> native_tip_span{};
        const auto number = [](const char* raw) {
            double value;
            const std::string_view word = raw;
            const auto [end, err] = std::from_chars(word.data(), word.data() + word.size(), value);
            if (err != std::errc() || end != word.data() + word.size() || !std::isfinite(value))
                throw std::runtime_error("invalid numeric argument");
            return value;
        };
        for (int n = 3; n < argc; ++n) {
            const std::string_view flag = argv[n];
            if (flag == "--base-nozzle") windows.push_back({45, 73, 125, 213});
            else if (flag == "--nozzle-box" && n + 4 < argc) {
                std::array<double, 4> box;
                for (double &field : box) field = number(argv[++n]);
                if (box[0] >= box[2] || box[1] >= box[3]) throw std::runtime_error("nozzle box must have positive area");
                if ((box[2] - box[0]) * (box[3] - box[1]) > bed_x*bed_y)
                    throw std::runtime_error("nozzle box exceeds the plate area");
                windows.push_back(box);
            } else if (flag == "--native-tip-shoulder" && n + 2 < argc) {
                for (double &height : native_tip_span) height = number(argv[++n]);
                if (native_tip_span[0] >= native_tip_span[1]) throw std::runtime_error("invalid native-tip span");
            } else throw std::runtime_error("unrecognized option " + std::string(flag));
        }
        std::ifstream f(argv[1]);
        if (!f) throw std::runtime_error("cannot read G-code");
        Replay replay(argv[2], windows);
        if (native_tip_span[1]) {
            replay.native_tip_low = native_tip_span[0];
            replay.native_tip_high = native_tip_span[1];
            replay.native_tip_phase = "native tip in shoulder height band";
        }
        replay.read(f);
        output(std::cout, replay);
    } catch (const std::exception& err) {
        std::cerr << err.what() << '\n';
        return 1;
    }
}
