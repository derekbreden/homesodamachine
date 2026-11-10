#!/usr/bin/env bash
# look.sh — see a body in the pack, from the three orthographic directions, in one command.
#
# `hsm render --look` takes a step path relative to hardware/, an output path, a projection, a
# context mode and a size — five arguments with one right answer each, where a wrong path root
# names a payload that is not there. This fixes every argument that has a right answer and leaves
# the ones a caller actually chooses: which bodies to look at, and what to ask about them.
#
#   tools/look.sh seaflo-pump                 # one body, three views
#   tools/look.sh fluid-23,fluid-27           # a pair — the shape a crossing shows up in
#   tools/look.sh 'divider-y-*' --views top   # a glob, plan only
#   tools/look.sh --near wr1110               # the body AND its neighbourhood, ranked
#   tools/look.sh --near wr1110 --within 40   # a wider neighbourhood
#   tools/look.sh --vs tube-water-6,tube-water-7   # two bodies side by side at ONE scale
#   tools/look.sh --list                      # every body name in the pack
#   tools/look.sh --check                     # which looks already taken have gone stale
#
# Named bodies render SOLID with feature edges and a tint each; everything else stays IN FRAME as
# edges only, so a neighbour is visible without hiding the subject. The frame carries a mm grid
# with numbered ticks and a scale bar measured through the projection used, so a coordinate is
# read off the picture rather than trusted from a table — which is the whole point, since the
# tables report bounding boxes and a bounding box is a rectangle, not a part.
#
# THE FRAME IS ALSO THE CHECK: a name is the name of the thing you meant only when the thing that
# lit up is the thing you meant. Look at the frame before you quote the name.
#
# --near ranks exported bodies through `hsm around`: catalog bounds prefilter the candidates,
# and selected mesh pairs supply their solid clearances. Unresolved candidates remain visible
# and named as unresolved. The subject is amber; the walls stay x-ray. Its box plus the requested
# radius frames the neighbourhood. The ranked list and legend carry the same payload reading.
#
# --vs FRAMES EACH OF TWO BODIES ON ITSELF and joins the two frames at one span, so a millimetre
# is the same length in both halves and the two shapes are read against each other rather than
# against their own boxes. Broken symmetry is a thing no table in this repo reports and a twin
# frame reports in one glance: the bend one has and the other has not, the arm that is shorter,
# the mirror that is not a mirror.
#
# Beside every PNG goes `<png>.scene.json` — the line that redraws it, and every repo file whose
# text could decide the picture, each with the hash of its bytes. `--check` hashes them again and
# says which looks have gone stale under the machine's next build.
#
# Prints the paths it wrote. Read them.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STEP="manifold-layout/enclosure-assembly.step"
VIEWS="top,front,right"
SIZE="1600x1200"
OUT="${TMPDIR:-/tmp}/look"
HSM="${HSM_BIN:-$(command -v hsm || echo "$HOME/.local/bin/hsm")}"

usage() { awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "${BASH_SOURCE[0]}"; }
die() { echo "look: $*" >&2; exit 2; }
render() { "$REPO/tools/run" -- "$HSM" --root "$REPO" render "$@"; }

only=""
near=""
vs=""
within="25"
list=""
check=""
extra=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --list)    list=1; shift ;;
    --check)   check=1; shift ;;
    --near)    near="$2"; shift 2 ;;
    --near=*)  near="${1#*=}"; shift ;;
    --within)  within="$2"; shift 2 ;;
    --within=*) within="${1#*=}"; shift ;;
    --vs)      vs="$2"; shift 2 ;;
    --vs=*)    vs="${1#*=}"; shift ;;
    --views)   VIEWS="$2"; shift 2 ;;
    --views=*) VIEWS="${1#*=}"; shift ;;
    --step)    STEP="$2"; shift 2 ;;
    --step=*)  STEP="${1#*=}"; shift ;;
    --size)    SIZE="$2"; shift 2 ;;
    --size=*)  SIZE="${1#*=}"; shift ;;
    --out)     OUT="$2"; shift 2 ;;
    --out=*)   OUT="${1#*=}"; shift ;;
    --help|-h) usage; exit 0 ;;
    --)        shift; extra+=("$@"); break ;;
    -*)        extra+=("$1"); shift ;;          # anything else goes straight to hsm render
    *)         only="$1"; shift ;;
  esac
done

if [[ -n "$list" ]]; then
  render "$STEP" --list
  exit
fi

if [[ -n "$check" ]]; then
  exec node "$REPO/tools/look-record.js" check "$OUT"
fi

asked=0
for m in "$only" "$near" "$vs"; do
  if [[ -n "$m" ]]; then asked=$((asked + 1)); fi
done
[[ $asked -le 1 ]] || die "one subject at a time: a name, or --near <body>, or --vs <a>,<b>"
if [[ $asked -eq 0 ]]; then
  usage
  exit 2
fi

mkdir -p "$OUT"
# One stem per QUESTION, so two looks do not overwrite each other and both stay readable side by
# side. Globs, commas and spaces are not filename characters.
stem_for() { printf '%s/%s.png' "$OUT" "$(printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '-')"; }

# The frames a --views render writes beside the stem it was given.
frames=()
plan_frames() {
  local stem="$1" v
  frames=()
  for v in ${VIEWS//,/ }; do frames+=("${stem%.png}.$v.png"); done
}

# The pack's name-and-box table, read once. A frame that has to hold something other than its own
# solid set — a neighbourhood, or a second body at the same scale — is spanned off these numbers.
boxes=""
box_table() {
  if [[ -z "$boxes" ]]; then boxes="$(render "$STEP" --list)"; fi
}

# `<half-span> <centre>` for one named body, the half-span grown by the margin given. The row is
# `name x[lo,hi] y[lo,hi] z[lo,hi]`; stripping the axis letters and the brackets leaves numbers.
fit_to() {
  awk -v N="$1" -v PAD="$2" '
    $1 == N {
      line = $0; gsub(/[xyz]\[/, " ", line); gsub(/[],]/, " ", line); split(line, f)
      m = f[3]-f[2]; if (f[5]-f[4] > m) m = f[5]-f[4]; if (f[7]-f[6] > m) m = f[7]-f[6]
      printf "%.3f %.3f,%.3f,%.3f", m/2 * 1.15 + PAD, (f[2]+f[3])/2, (f[4]+f[5])/2, (f[6]+f[7])/2
      found = 1
      exit
    }
    END { if (!found) exit 3 }' <<<"$boxes"
}

# The line that redraws this picture. It goes in the record and `--check` prints it back.
command_line=""
also=()

if [[ -n "$near" ]]; then
  stem="$(stem_for "$near-near")"
  command_line="tools/look.sh --near $near --within $within --views $VIEWS --size $SIZE --step $STEP"
  also=(--also tools/hsm/engine/src --also tools/hsm/geometry/src)

  echo "reading $near — exported solid clearances within $within mm…" >&2
  found="$("$HSM" --root "$REPO" --scene "$STEP" around "$near" --within "$within")"
  neighborhood=()
  while IFS= read -r -d '' value; do neighborhood+=("$value"); done < <(
    printf '%s' "$found" | node "$REPO/tools/look-record.js" near-plan
  )
  [[ ${#neighborhood[@]} -eq 6 ]] || die "native neighborhood returned no frame"
  span="${neighborhood[0]}"
  target="${neighborhood[1]}"
  subject="${neighborhood[2]}"
  ranked="${neighborhood[3]}"
  printf '%s\n\n' "${neighborhood[5]}"

  plan_frames "$stem"
  render "$STEP" "$stem" --look --views "$VIEWS" \
    --span "$span" --target "$target" --size "$SIZE" \
    --only "${ranked:+$ranked,}$subject" --xray "enclosure-*" --select "$subject" \
    --caption "${neighborhood[4]}" "${extra[@]+"${extra[@]}"}"

elif [[ -n "$vs" ]]; then
  IFS=, read -r a b rest <<<"$vs"
  [[ -n "$a" && -n "$b" && -z "$rest" ]] || die "--vs takes exactly two body names: --vs a,b"
  stem="$(stem_for "$a-vs-$b")"
  command_line="tools/look.sh --vs $a,$b --views $VIEWS --size $SIZE --step $STEP"

  # ONE SPAN FOR BOTH HALVES. A render fits the frame to its own subject, so two subjects rendered
  # apart come back at two scales and the picture lies about which is bigger. Both boxes are read
  # off the pack first and the larger one sets the span each half is drawn at.
  box_table
  fa="$(fit_to "$a" 0)" || die "no body $a in the pack; tools/look.sh --list has them all"
  fb="$(fit_to "$b" 0)" || die "no body $b in the pack; tools/look.sh --list has them all"
  span="$(awk '{print ($1 > $2) ? $1 : $2}' <<<"${fa%% *} ${fb%% *}")"

  # The halves are drawn outside $OUT: they are the twin's material, not looks of their own.
  work="${TMPDIR:-/tmp}/look-halves.$$"
  mkdir -p "$work"
  trap 'rm -rf "$work"' EXIT
  for side in "a:$a:$b" "b:$b:$a"; do
    IFS=: read -r tag me other <<<"$side"
    render "$STEP" "$work/$tag.png" --look --views "$VIEWS" \
      --span "$span" --only "$me" --xray "enclosure-*" --size "$SIZE" \
      --caption "twin at one span — this half is $me, beside it $other" \
      "${extra[@]+"${extra[@]}"}"
  done

  plan_frames "$stem"
  for v in ${VIEWS//,/ }; do
    render --twin "${stem%.png}.$v.png" "$work/a.$v.png" "$work/b.$v.png"
  done

else
  stem="$(stem_for "$only")"
  command_line="tools/look.sh '$only' --views $VIEWS --size $SIZE --step $STEP"
  plan_frames "$stem"
  render "$STEP" "$stem" --look --views "$VIEWS" --ortho \
    --only "$only" --xray "enclosure-*" --size "$SIZE" "${extra[@]+"${extra[@]}"}"
fi

node "$REPO/tools/look-record.js" write --step "$STEP" \
  --command "$command_line" "${also[@]+"${also[@]}"}" "${frames[@]}"

echo
echo "read:"
printf '  %s\n' "${frames[@]}"
