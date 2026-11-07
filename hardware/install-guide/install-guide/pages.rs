//! What the booklet says and shows, page by page: the covers and the numbered interior pages.
use super::book::*;
use super::slots::mounting_slots;
use anyhow::{Context, Result};
use hsm_pages::{reads, Rgb, Target};
use serde_json::Value;

const BEFORE: &str = "BEFORE YOU START";

/// A registered anchor of a picture, in its reference pixels.
fn anchor(book: &Book, picture: &str, name: &str) -> Result<[f64; 2]> {
    let a = &book.resolutions[picture]["anchors_reference_pixels"][name];
    Ok([a[0].as_f64().context("an anchor")?, a[1].as_f64().context("an anchor")?])
}

fn front_cover(b: &mut Book) -> Result<()> {
    b.page_no = 1;
    b.ground(BLUE);
    b.label("HOME SODA MACHINE", 52.0, 51.0, WHITE, 11.0);
    b.text("Install", 52.0, 145.0, 60.0, Face::Bold, WHITE)?;
    b.text("guide", 52.0, 211.0, 60.0, Face::Bold, WHITE)?;
    b.mark(BLUE, 373.0, H - 295.0, 222.0)?;
    b.rect(52.0, 311.0, 64.0, 5.0, ORANGE, None, 0.0);
    b.para(Para::new("From the box<br/>to your first glass.", 52.0, 345.0, 328.0).size(23.0, 30.0).color(WHITE).limit(60.0))?;
    b.text("SEVEN STEPS. EVERY CONNECTION.", 52.0, 445.0, 9.0, Face::Semibold, ICE)?;
    b.text("homesodamachine.com", 425.0, 445.0, 10.0, Face::Regular, WHITE)?;
    b.outline.push(("Cover".into(), 0));
    b.show();
    Ok(())
}

fn back_cover(b: &mut Book) -> Result<()> {
    b.page_no += 1;
    b.ground(BLUE);
    b.label("HOME SODA MACHINE", 52.0, 51.0, WHITE, 11.0);
    b.mark(BLUE, 44.0, H - 280.0, 216.0)?;
    b.text("On tap.", 313.0, 136.0, 51.0, Face::Bold, WHITE)?;
    b.rect(315.0, 212.0, 57.0, 5.0, ORANGE, None, 0.0);
    b.para(Para::new("Keep this guide<br/>with your install kit.", 315.0, 251.0, 277.0).size(23.0, 30.0).color(WHITE).limit(60.0))?;
    b.para(
        Para::new(
            "<b>Sealed cooling circuit</b><br/>R-600a (isobutane), flammable refrigerant.<br/>Under 1.5 oz (40 g). Do not open, puncture or heat.",
            52.0,
            357.0,
            540.0,
        )
        .size(10.5, 15.0)
        .color(ICE)
        .limit(60.0),
    )?;
    b.text("homesodamachine.com", 52.0, 438.0, 15.0, Face::Semibold, WHITE)?;
    b.text("Guides: /drawings", 455.0, 442.0, 10.0, Face::Regular, ICE)?;
    b.link([52.0, H - 459.0, 301.0, H - 435.0], Target::Uri("https://homesodamachine.com".into()));
    b.link([450.0, H - 458.0, 600.0, H - 435.0], Target::Uri("https://homesodamachine.com/drawings".into()));
    b.outline.push(("Back cover".into(), b.page_no - 1));
    b.show();
    Ok(())
}

/// Every page, front cover to back.
pub fn compose(b: &mut Book) -> Result<()> {
    let fill: Value = serde_json::from_str(&reads::text(b.asset("fill-scene-inputs.json"))?)?;
    let pose = |key: &str| -> Result<[f64; 3]> {
        let v = &fill["pose"][key];
        Ok([0, 1, 2].map(|i| v[i].as_f64().unwrap_or(f64::NAN))).and_then(|p| {
            anyhow::ensure!(p.iter().all(|v| v.is_finite()), "fill-scene-inputs.json: pose {key}");
            Ok(p)
        })
    };
    let (fill_cam, fill_target) = (pose("cam")?, pose("target")?);
    let fill_span = fill["pose"]["span"].as_f64().context("fill-scene-inputs.json: pose span")?;

    front_cover(b)?;

    // Interior 1
    b.header("Your first glass starts here", BEFORE, None, Some("Keep this booklet beside you while you install. Follow the seven steps in order."))?;
    b.pic("steps/pour-base.png", M, 145.0, 260.0, 271.0, Some([150.0, 40.0, 1475.0, 1500.0]), true)?;
    b.text("Make the connections.", RIGHT, 158.0, 18.0, Face::Bold, NAVY)?;
    b.para(Para::new("Start with the faucet and cold-water supply. Match each tube to its color on the back of the machine.", RIGHT, 190.0, RW))?;
    b.text("Fill both flavors.", RIGHT, 271.0, 18.0, Face::Bold, NAVY)?;
    b.para(Para::new("Use one concentrate bottle for each reservoir. The display walks you through Fill.", RIGHT, 304.0, RW))?;
    b.para(
        Para::new("<b>Then chill, choose and pour.</b><br/>The first chill takes about an hour. Fill your glass with ice before pouring.", RIGHT, 373.0, RW)
            .size(12.0, 17.0)
            .limit(68.0),
    )?;
    b.end()?;

    // Interior 2
    b.header("Your route to soda", BEFORE, None, Some("Follow the seven steps in order. Page numbers below refer to this booklet."))?;
    let route = [
        (1, "Mount the faucet", "5-8", 5),
        (2, "Add the cold-water tee", "9-16", 9),
        (3, "Match the rear connections", "17-18", 17),
        (4, "Prepare the cylinder", "19-21", 19),
        (5, "Water, then gas, then power", "22-24", 22),
        (6, "Fill both flavors", "25-27", 25),
        (7, "Chill. Choose. Pour.", "28-29", 28),
    ];
    for (i, (number, title, pages, target)) in route.into_iter().enumerate() {
        let y = 145.0 + i as f64 * 36.0;
        b.badge(number, M, y, 11.0)?;
        b.text(title, M + 35.0, y + 3.0, 13.0, Face::Semibold, NAVY)?;
        let w = b.width(pages, Face::Regular, 11.0);
        b.text(pages, 327.0 - w, y + 4.0, 11.0, Face::Regular, MUTED)?;
        // The page the step starts on, by its index: interior pages follow the cover.
        b.link([M, H - y - 25.0, 333.0, H - y + 2.0], Target::Page(target));
    }
    b.note("BEFORE THE FIRST CONNECTION", "Check the kit and space on pages 3-4. Keep the cylinder closed and the power cord unplugged while you install.", 149.0, RIGHT, RW, false)?;
    b.note("KEEP THIS GUIDE", "Care is on page 30. Connection checks are on pages 31-32.", 334.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 3
    b.header("Have everything ready", BEFORE, None, Some("Unpack the kit. Have your own supplies ready before opening a water connection."))?;
    b.label("IN THE BOX", M, 134.0, BLUE, 9.0);
    let kit = [
        ("machine", "Soda machine"),
        ("faucet-and-plate", "Faucet +<br/>mounting plate"),
        ("filtered-line", "Filtered water line"),
        ("water-tees", "Both water tees"),
        ("regulator-and-tether", "Regulator + CO2 tether<br/>+ nylon washer"),
        ("collet-press", "Collet press"),
        ("power-cord", "Power cord"),
        ("install-guide", "Install guide"),
        ("cold-kit", "Cold kit"),
    ];
    for (i, (art, title)) in kit.into_iter().enumerate() {
        let (x, y) = (M + (i % 3) as f64 * 136.0, 149.0 + (i / 3) as f64 * 99.0);
        let title_height = if title.contains("<br/>") { 25.0 } else { 12.5 };
        let caption_height = title_height + if art == "cold-kit" { 13.0 } else { 0.0 };
        let caption_y = y + 90.0 - 7.0 - caption_height;
        b.rect(x, y, 128.0, 90.0, WHITE, Some(RULE), 4.0);
        b.kit_picture(art, x + 8.0, y + 5.0, 112.0, caption_y - y - 10.0)?;
        b.para(Para::new(title, x + 8.0, caption_y, 112.0).size(10.5, 12.5).face(Face::Semibold).limit(title_height).centred())?;
        if art == "cold-kit" {
            b.para(Para::new("Keep bagged for later.", x + 8.0, caption_y + title_height + 1.0, 112.0).size(9.0, 12.0).color(MUTED).centred())?;
        }
    }
    b.rect(459.0, 144.0, 145.0, 295.0, Rgb::hex("#F2F5FB"), None, 6.0);
    b.label("YOU SUPPLY", 473.0, 159.0, NAVY, 8.0);
    let supplies = [
        "Filled 5 lb CO2 cylinder<br/>(CGA-320)",
        "Concentrate for both flavors<br/>(SodaStream compatible)",
        "Adjustable wrench",
        "Second wrench for a braided hose",
        "Towel",
        "Prepared counter opening",
        "Grounded 120 V outlet",
    ];
    let mut y = 181.0;
    for entry in supplies {
        b.rect(473.0, y + 2.0, 8.0, 8.0, WHITE, Some(MUTED), 1.0);
        let h = b.para(Para::new(entry, 488.0, y, 103.0).size(10.0, 13.0).limit(52.0))?;
        y += h + 11.0;
    }
    b.end()?;

    // Interior 4
    b.header("Make room under the counter", BEFORE, None, Some("Leave the cylinder valve, water shutoff and power plug easy to reach."))?;
    b.rect(65.0, 152.0, 237.0, 224.0, ICE, None, 6.0);
    b.rect(97.0, 179.0, 172.0, 194.0, Rgb::hex("#E8EBF0"), Some(INK), 4.0);
    b.rect(110.0, 292.0, 146.0, 68.0, Rgb::hex("#D8DCE3"), Some(MUTED), 3.0);
    b.text("TOP VIEW", 150.0, 229.0, 11.0, Face::Semibold, MUTED)?;
    b.text("Front", 165.0, 391.0, 11.0, Face::Regular, MUTED)?;
    b.text("Machine envelope", RIGHT, 152.0, 17.0, Face::Bold, NAVY)?;
    b.para(Para::new("<b>8-1/2 in wide</b><br/><b>18-3/8 in deep</b><br/><b>14-3/8 in tall, with cover</b>", RIGHT, 187.0, RW).size(13.0, 20.0))?;
    b.para(Para::new("Leave <b>2-3/8 in behind</b> and <b>1-5/8 in on each side.</b> Keep the side air paths open.", RIGHT, 268.0, RW))?;
    b.para(
        Para::new(
            "Above: room to tip a bottle just past level over the funnel.<br/><br/>Beside it: space for the cylinder, about 5-1/4 in across and 18 in tall, plus its regulator.",
            RIGHT,
            338.0,
            RW,
        )
        .size(12.0, 17.0)
        .limit(102.0),
    )?;
    b.end()?;

    // Interior 5
    let mount = "INSTALL / MOUNT THE FAUCET";
    b.header("Prepare the counter opening", mount, Some(1), None)?;
    b.pic("opening.png", M, 151.0, 264.0, 220.0, None, true)?;
    b.text("One 1-3/8 in opening", RIGHT, 158.0, 18.0, Face::Bold, NAVY)?;
    b.para(
        Para::new(
            "Place the hole center <b>at most 2 in behind the bowl edge.</b> Aim the faucet into the bowl, within 10 degrees of straight ahead.",
            RIGHT,
            194.0,
            RW,
        )
        .size(12.0, 17.0)
        .limit(133.0),
    )?;
    b.note("STONE COUNTER", "Use a spare 1-3/8 in sink or counter hole, or a 1-3/8 in diamond core bit kept wet.", 351.0, RIGHT, RW, false)?;
    b.caption("Prepare the opening before lowering the faucet.", 390.0, M, 264.0)?;
    b.end()?;

    // Interior 6
    b.header("Lower. Then push back.", mount, Some(1), None)?;
    let p = b.pic("steps/mount-drop.png", M, 125.0, 274.0, 294.0, Some([9.0, 33.0, 763.0, 1331.0]), true)?;
    b.arrow(&[p.at([190.0, 660.0]), p.at([190.0, 963.0])], 11.0);
    b.arrow(&[p.at([382.0, 866.0]), p.at([585.0, 928.0])], 10.0);
    b.item("1 / LOWER", "Feed the tails through", "Pass all four attached tubes and the display cable through the opening. The small white tube is DRAIN. Lower the faucet onto the counter.", 151.0, RIGHT, RW, 13.0)?;
    b.item("2 / POSITION", "Push the faucet back", "Push it away from you until the rear tube bundle meets the back edge of the hole. Hold that position for the plate.", 299.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 7
    b.header("Slide the plate into place", mount, Some(1), None)?;
    let p = b.pic("steps/mount-under-slide-clean.png", M, 132.0, 278.0, 126.0, Some([205.0, 280.0, 1090.0, 650.0]), true)?;
    b.arrow(&[p.at([430.0, 540.0]), p.at([870.0, 455.0])], 10.0);
    b.caption("The plate sits above the washer and nut.", 261.0, M, 264.0)?;
    b.item("3 / FROM BELOW", "Hold the plate flat", "Hold the steel plate flat against the counter, above the washer and nut. Slide it onto the shank and rear bundle.", 132.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Match the slots as shown below.", RIGHT, 250.0, RW).size(12.0, 17.0).limit(17.0))?;
    mounting_slots(b)?;
    b.end()?;

    // Interior 8
    b.header("Tighten the faucet nut", mount, Some(1), None)?;
    b.pic("steps/mount-under-tighten-clean.png", M, 132.0, 278.0, 126.0, Some([740.0, 310.0, 1180.0, 610.0]), true)?;
    b.caption("The plate stays above the washer and nut.", 261.0, M, 264.0)?;
    b.item("4 / SECURE", "Hand-tighten the nut", "Keep the plate flat against the counter and the faucet pushed back. Hand-tighten the nut against the washer.", 132.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Keep the neck-joint drain opening entirely over the bowl and uncovered.", RIGHT, 244.0, RW).size(11.0, 14.0).limit(28.0))?;
    mounting_slots(b)?;
    b.end()?;

    // Interior 9
    b.header("Which water connection?", "INSTALL / ADD THE COLD-WATER TEE", Some(2), Some("Look at the cold supply under your sink. Use the tee that matches it."))?;
    b.pic("kitchen-push.png", M, 145.0, 225.0, 121.0, None, true)?;
    b.text("1/4 in plastic tube", M, 286.0, 18.0, Face::Bold, NAVY)?;
    b.para(Para::new("A small tube in a push fitting, like a filter or refrigerator line. Use the <b>black tee</b>.", M, 321.0, 258.0))?;
    b.text("Continue on pages 10-12", M, 403.0, 12.0, Face::Bold, BLUE)?;
    b.pic("kitchen-hose.png", RIGHT, 145.0, RW, 121.0, None, true)?;
    b.text("Braided hose", RIGHT, 286.0, 18.0, Face::Bold, NAVY)?;
    b.para(Para::new("A braided supply hose threaded onto a <b>3/8 in shutoff</b>. Use the <b>white tee</b>.", RIGHT, 321.0, RW))?;
    b.text("Continue on pages 13-16", RIGHT, 403.0, 12.0, Face::Bold, BLUE)?;
    b.end()?;

    // Interior 10
    let push = "INSTALL / PLASTIC-TUBE CONNECTION";
    b.header("Close the cold-water shutoff", push, Some(2), None)?;
    b.pic("steps/modern-water-off.png", M, 167.0, 278.0, 169.0, Some([170.0, 190.0, 1100.0, 635.0]), true)?;
    b.caption("Keep the shutoff closed while making connections.", 368.0, M, 264.0)?;
    b.item("1 / WATER OFF", "Wait for flow to stop", "Close the cold-water shutoff. Run the tap or dispenser on that line until flow stops.", 156.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Put a towel beneath the fitting to catch the water left in the tube.", RIGHT, 318.0, RW))?;
    b.end()?;

    // Interior 11
    b.header("Release the original tube", push, Some(2), None)?;
    let p = b.pic("steps/release-with-press.png", M, 173.0, 278.0, 173.0, Some([0.0, 0.0, 1840.0, 1040.0]), true)?;
    b.arrow(&[p.at([1316.97, 779.94]), p.at([1042.29, 700.52])], 8.0);
    b.arrow(&[p.at([1510.0, 554.0]), p.at([1780.0, 632.0])], 8.0);
    b.item("2 / RELEASE", "Hold the ring in", "Use the collet press to hold the fitting's release ring in. With your other hand, pull the original white tube out.", 153.0, RIGHT, RW, 13.0)?;
    b.note("KEEP THE TOOL", "The collet press also releases the machine's push-connect tubes when their pressure has been relieved.", 321.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 12
    b.header("Fit the black tee", push, Some(2), None)?;
    let p = b.pic("steps/modern-tee-assembly-ready.png", M, 145.0, 278.0, 90.0, Some([200.0, 130.0, 1860.0, 670.0]), true)?;
    b.arrow(&[p.at([1110.0, 170.0]), p.at([810.0, 170.0])], 9.0);
    b.pic("steps/modern-tee-complete.png", M, 286.0, 278.0, 90.0, Some([200.0, 130.0, 1860.0, 670.0]), true)?;
    b.item("3 / JUMPER", "Push it fully home", "Push the short jumper on the supplied black tee into the fitting you opened.", 137.0, RIGHT, RW, 13.0)?;
    b.item("4 / ORIGINAL TUBE", "Reconnect. Then tug.", "Push the original tube into the tee's open end. Tug both joints gently to check they hold.", 281.0, RIGHT, RW, 13.0)?;
    b.caption("Keep the filtered white run attached. Go to page 17.", 403.0, M, CW)?;
    b.end()?;

    // Interior 13
    let hose = "INSTALL / BRAIDED-HOSE CONNECTION";
    b.header("Prepare the braided-hose connection", hose, Some(2), None)?;
    b.pic("two-tees.png", M, 162.0, 274.0, 121.0, None, true)?;
    b.caption("The white tee has a side-port lever.", 315.0, M, 264.0)?;
    b.item("1 / FIND COLD", "Trace the hose to its valve", "The white tee fits a 3/8 in outlet. Close that valve, then open the kitchen faucet on cold. Wait for flow to stop.", 145.0, RIGHT, RW, 13.0)?;
    b.note("BEFORE LOOSENING", "If water keeps flowing, leave the hose connected; the shutoff needs repair. Put a towel below the connection.", 321.0, RIGHT, RW, true)?;
    b.end()?;

    // Interior 14
    b.header("Lift the braided hose clear", hose, Some(2), None)?;
    b.pic("hose-attached.png", M, 135.0, 130.0, 215.0, Some([270.0, 0.0, 820.0, 940.0]), true)?;
    b.pic("hose-removed.png", 192.0, 135.0, 130.0, 215.0, Some([270.0, 0.0, 820.0, 940.0]), true)?;
    b.caption("Valve closed", 369.0, M, 130.0)?;
    b.caption("Hose lifted clear", 369.0, 192.0, 130.0)?;
    b.item("2 / TWO WRENCHES", "Hold the valve steady", "Use one wrench on the valve body while the other loosens the hose nut. Keep the valve from twisting on its pipe.", 153.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Finish unscrewing the nut by hand. Lift the hose away and catch the water left in it.", RIGHT, 319.0, RW))?;
    b.end()?;

    // Interior 15
    b.header("Fit the white tee", hose, Some(2), None)?;
    b.pic("tee-after.png", M, 137.0, 264.0, 269.0, None, true)?;
    b.item("3 / TEE ONTO VALVE", "Start the lower nut by hand", "Thread the tee's lower nut onto the shutoff outlet. Keep the valve body steady.", 144.0, RIGHT, RW, 13.0)?;
    b.item("4 / HOSE ONTO TEE", "Reconnect the braided hose", "Start the hose nut on the tee's top by hand. Hold the tee steady and nip both joints up: snug, then a little more.", 291.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 16
    b.header("Move the white filtered run", hose, Some(2), None)?;
    b.pic("filter-in-cabinet.png", M, 164.0, 274.0, 179.0, None, true)?;
    b.caption("Keep the filter and its tube collar on the run.", 371.0, M, 264.0)?;
    b.item("5 / MOVE THE RUN", "Release it from the black tee", "Use the collet press on the black tee's branch. Its short jumper and the black tee are not used on this path.", 146.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Push the filtered white run fully into the white tee's side port, then tug gently. Leave the small side-port lever open.", RIGHT, 294.0, RW))?;
    b.text("Keep the main shutoff closed.", RIGHT, 396.0, 12.0, Face::Bold, BLUE)?;
    b.end()?;

    // Interior 17
    let rear = "INSTALL / MATCH THE REAR CONNECTIONS";
    b.header("Match the rear connections", rear, Some(3), None)?;
    let p = b.pic("steps/the-back-face.png", M, 148.0, 282.0, 253.0, Some([160.0, 20.0, 1440.0, 1120.0]), true)?;
    let jack = anchor(b, "steps/the-back-face.png", "jack-port")?;
    b.leader("DATA / Faucet cable", M, 136.0, p.at(jack))?;
    b.para(Para::new("Pull off the <b>CO2 and TAP shipping caps.</b> They cover the fittings; leave the fittings mounted.", RIGHT, 136.0, RW).size(12.0, 17.0).limit(68.0))?;
    let rows = [
        ("CO2", "Top left / red tube from the cylinder", Rgb::hex("#D7333C"), WHITE),
        ("TAP", "Top right / larger white filter tube", WHITE, INK),
        ("SODA", "Middle left / blue faucet tube", Rgb::hex("#1670DB"), WHITE),
        ("DRAIN", "Bottom left / small white 4 mm tube", WHITE, INK),
        ("FLAVOR", "Right column / black tubes; either port", INK, WHITE),
    ];
    for (i, (name, desc, bg, fg)) in rows.into_iter().enumerate() {
        let y = 215.0 + i as f64 * 43.0;
        b.rect(RIGHT, y, 71.0, 23.0, bg, (bg == WHITE).then_some(RULE), 3.0);
        b.text(name, RIGHT + 8.0, y + 6.0, 10.0, Face::Bold, fg)?;
        b.text(desc, RIGHT, y + 29.0, 11.0, Face::Regular, INK)?;
    }
    b.end()?;

    // Interior 18
    b.header("Push home. Then tug.", rear, Some(3), None)?;
    b.pic("steps/connect-rear-open.png", M, 155.0, 283.0, 183.0, Some([60.0, 160.0, 1350.0, 880.0]), true)?;
    b.caption("Push straight into the fitting, all the way to its stop.", 362.0, M, 264.0)?;
    b.item("CHECK EVERY TUBE", "Push to its stop", "Match each tube label to its port. A fitting can grip before the tube reaches the seal. Push fully home, then tug gently.", 144.0, RIGHT, RW, 13.0)?;
    b.para(
        Para::new(
            "<b>Click the faucet cable into DATA.</b><br/><br/>Leave the DRAIN tube at its factory length. Lay the filter flat and route all tails in loose curves, clear of things that slide in and out.",
            RIGHT,
            303.0,
            RW,
        )
        .size(12.0, 17.0)
        .limit(136.0),
    )?;
    b.end()?;

    // Interior 19
    let cylinder = "TURN IT ON / PREPARE THE CYLINDER";
    b.header("Prepare the CO2 cylinder", cylinder, Some(4), None)?;
    b.pic("steps/co2-ready.png", M, 135.0, 278.0, 279.0, Some([0.0, 0.0, 1560.0, 1500.0]), true)?;
    b.item("1 / CYLINDER", "Stand it upright", "Use a filled 5 lb cylinder with a CGA-320 connection. Stand it beside the machine with its valve closed.", 146.0, RIGHT, RW, 13.0)?;
    b.note("PRESSURE IS ALREADY SET", "The supplied regulator is set at the factory. Leave its adjusting screw and locknut alone.", 315.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 20
    b.header("Attach the supplied regulator", cylinder, Some(4), None)?;
    b.pic("steps/co2-ready.png", M, 137.0, 278.0, 266.0, Some([0.0, 0.0, 1560.0, 1500.0]), true)?;
    b.item("2 / CGA-320 NUT", "One washer, lying flat", "Place one supplied nylon washer flat inside the large nut. Start the nut squarely on the closed cylinder outlet by hand.", 146.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("Snug it with the wrench. Extra force can damage the washer.", RIGHT, 282.0, RW).size(12.0, 17.0).limit(51.0))?;
    b.note("REGULATOR + TETHER", "The outlet adapter and red tether arrive fitted to the regulator. Keep them assembled.", 341.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 21
    b.header("Connect the red tether", cylinder, Some(4), None)?;
    let p = b.pic("steps/connect-rear-open.png", M, 156.0, 278.0, 230.0, Some([60.0, 160.0, 1350.0, 880.0]), true)?;
    let (tube, mouth) = (anchor(b, "steps/connect-rear-open.png", "co2-tube")?, anchor(b, "steps/connect-rear-open.png", "co2-mouth")?);
    b.arrow(&[p.at(tube), p.at(mouth)], 10.0);
    b.caption("Keep the regulator end of the tether assembled.", 402.0, M, 264.0)?;
    b.item("3 / CO2 PORT", "Red tube to red fitting", "Push the free end of the red tether into the machine's red CO2 port. Push fully home, then tug gently.", 153.0, RIGHT, RW, 13.0)?;
    b.note("KEEP THE CYLINDER CLOSED", "Finish all connections before opening water or gas. The next pages take you through water, gas and power in that order.", 319.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 22
    let turn_on = "TURN IT ON / WATER, GAS, POWER";
    b.header("First, open the water", turn_on, Some(5), None)?;
    b.pic("steps/modern-water-on.png", M, 158.0, 278.0, 176.0, Some([170.0, 190.0, 1100.0, 635.0]), true)?;
    b.caption("Plastic-tube valve: its open handle follows the tube.", 365.0, M, 264.0)?;
    b.item("1 / WATER", "Open the shutoff slowly", "On the braided-hose path, check that the white tee's small side-port lever is open too.", 141.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("<b>Watch for a full minute.</b><br/>Inspect the tee, filter ends and TAP connection. Keep power unplugged.", RIGHT, 267.0, RW).size(12.0, 17.0))?;
    b.note("IF YOU SEE WATER", "Close the shutoff. Resolve the leak before opening gas or connecting power. See page 31.", 342.0, RIGHT, RW, true)?;
    b.end()?;

    // Interior 23
    b.header("Then, open the gas", turn_on, Some(5), None)?;
    b.pic("steps/startup-gas.png", M, 138.0, 278.0, 269.0, None, true)?;
    b.item("2 / GAS", "Open the valve slowly", "Pressure is factory set. Leave the screw alone; the upper gauge settles near 75 PSI.", 144.0, RIGHT, RW, 12.0)?;
    b.para(
        Para::new("Listen at the cylinder nut, outlet and red CO2 port. A continuing hiss means a leak. Soapy water shows it as growing bubbles.", RIGHT, 251.0, RW)
            .size(12.0, 17.0)
            .limit(102.0),
    )?;
    b.note("BEFORE POWER", "If gas continues to escape, close the cylinder. Check page 32 and retest.", 342.0, RIGHT, RW, true)?;
    b.end()?;

    // Interior 24
    b.header("Finally, connect power", turn_on, Some(5), None)?;
    let p = b.pic("steps/power-ready.png", M, 164.0, 278.0, 194.0, Some([0.0, 160.0, 1800.0, 1140.0]), true)?;
    let (cord, socket) = (anchor(b, "steps/power-ready.png", "cord-approach")?, anchor(b, "steps/power-ready.png", "power-mouth")?);
    b.arrow(&[p.at(cord), p.at(socket)], 10.0);
    b.item("3 / POWER", "Connect the supplied cord", "Push it straight into the power socket at the upper right of the rear panel. Plug into a grounded 120 V outlet.", 144.0, RIGHT, RW, 13.0)?;
    b.para(Para::new("The machine chimes and its display starts. Follow the display if it reports an issue.", RIGHT, 296.0, RW))?;
    b.caption("120 V, 60 Hz; 5 A, 600 W. The inlet's 250 V marking describes the connector.", 396.0, M, CW)?;
    b.end()?;

    // Interior 25
    let fill_phase = "YOUR FIRST GLASS / FILL BOTH FLAVORS";
    b.header("Choose the flavor to fill", fill_phase, Some(6), None)?;
    b.pic("fill-screen-framed.png", M, 160.0, 278.0, 207.0, None, false)?;
    b.caption("Flavor 1 is selected. Fill and Start filling are separate controls.", 389.0, M, 264.0)?;
    b.item("1 / CHOOSE", "Tap a flavor on the left", "The large portrait shows the reservoir you selected.", 149.0, RIGHT, RW, 13.0)?;
    b.item("2 / OPEN FILL", "Tap Fill across the top", "Leave Start filling alone until the concentrate is in place on the next page.", 283.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 26
    b.header("Bottle first. Then start.", fill_phase, Some(6), None)?;
    let p = b.pic("steps/fill-ready.png", M, 133.0, 278.0, 279.0, Some([180.0, 480.0, 1360.0, 1500.0]), true)?;
    let cue: Vec<[f64; 2]> = fill["arrow"]
        .as_array()
        .context("fill-scene-inputs.json: arrow")?
        .iter()
        .map(|q| p.projected([0, 1, 2].map(|i| q[i].as_f64().unwrap_or(f64::NAN)), fill_cam, fill_target, fill_span))
        .collect();
    b.arrow(&cue, 10.0);
    b.item(
        "3 / ADD CONCENTRATE",
        "Lift off the funnel cover",
        "Wipe off water and debris. Lift by the front edge, then tip one whole 14.8&nbsp;fl&nbsp;oz (440&nbsp;mL) bottle just past level over the funnel until it empties.",
        146.0,
        RIGHT,
        RW,
        13.0,
    )?;
    b.item("4 / START", "Tap Start filling", "Let the machine draw the concentrate into the selected reservoir.", 309.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 27
    b.header("Wait for Filled. Then repeat.", fill_phase, Some(6), None)?;
    b.pic("steps/fill-closed.png", M, 130.0, 278.0, 282.0, Some([180.0, 480.0, 1360.0, 1500.0]), true)?;
    b.item("5 / FILLED", "Replace the funnel cover", "When the display says Filled, the concentrate is in the reservoir. Press the cover down until it rests evenly on the brim.", 145.0, RIGHT, RW, 13.0)?;
    b.item("6 / OTHER FLAVOR", "Repeat the same sequence", "Select the other image, open Fill, lift off the cover, pour in its bottle, then tap Start filling.", 295.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 28
    let glass = "YOUR FIRST GLASS";
    b.header("Allow the first chill", glass, Some(7), None)?;
    b.pic("steps/pour-base.png", M, 132.0, 278.0, 286.0, Some([150.0, 40.0, 1475.0, 1500.0]), true)?;
    b.label("FIRST CHILL", RIGHT, 152.0, BLUE, 9.0);
    b.text("About 1 hour", RIGHT, 185.0, 28.0, Face::Bold, NAVY)?;
    b.para(Para::new("Let the machine chill before your first pour.", RIGHT, 242.0, RW).size(15.0, 21.0))?;
    b.note("READY FOR YOUR GLASS", "Keep the water and cylinder supplies open. Choose your flavor at the faucet when you are ready to pour.", 330.0, RIGHT, RW, false)?;
    b.end()?;

    // Interior 29
    b.header("Choose. Ice. Pour.", glass, Some(7), None)?;
    let p = b.pic("steps/pour-base.png", M, 131.0, 278.0, 283.0, Some([150.0, 40.0, 1475.0, 1500.0]), true)?;
    // The pour picture's own camera.
    let (cam, target, span) = ([1.0, -1.8, 0.67], [0.0, -78.0, 119.0], 140.0);
    let tap = p.projected([0.0, -134.243, 211.599], cam, target, span);
    b.leader("Tap screen", M, 157.0, tap)?;
    let press = p.projected([0.0, -38.0, 39.0], cam, target, span);
    b.arrow(&[[press[0], press[1] - 26.0], [press[0], press[1] - 2.0]], 9.0);
    b.item("1 / CHOOSE", "Tap the faucet display", "Select a flavor. If the display is dim, the first tap wakes it.", 143.0, RIGHT, RW, 13.0)?;
    b.item("2 / POUR", "Fill your glass with ice", "Put it under the faucet and press the lever down. Release the lever to stop.", 284.0, RIGHT, RW, 13.0)?;
    b.end()?;

    // Interior 30
    b.header("Keep it ready", "AFTER INSTALLATION", None, None)?;
    b.text("Top up a flavor", M, 148.0, 17.0, Face::Bold, NAVY)?;
    b.para(
        Para::new("Use the Fill sequence on pages 25-27. If the display says <b>Full</b>, concentrate remains in the funnel. Add no more and replace the cover.", M, 180.0, 263.0)
            .size(12.0, 17.0)
            .limit(102.0),
    )?;
    b.text("Change a flavor", M, 280.0, 17.0, Face::Bold, NAVY)?;
    b.para(
        Para::new(
            "Fill the funnel with water first. Then select the old flavor, open Clean and tap Start cleaning; the water rinses the line below the funnel. When it finishes, fill the new flavor.",
            M,
            312.0,
            263.0,
        )
        .size(12.0, 17.0)
        .limit(68.0),
    )?;
    b.text("Rinse the funnel", RIGHT, 148.0, 17.0, Face::Bold, NAVY)?;
    b.para(
        Para::new("Rinse weekly and after changing flavors. Wash the removable silicone funnel and both faces of its cover by hand.", RIGHT, 180.0, RW)
            .size(12.0, 17.0)
            .limit(51.0),
    )?;
    b.para(
        Para::new(
            "Wipe the cover and lift it by its front edge. When the funnel is empty, lift it straight out. Its plug slides off the drain tube; the tube stays in the machine.",
            RIGHT,
            246.0,
            RW,
        )
        .size(12.0, 17.0)
        .limit(68.0),
    )?;
    b.para(
        Para::new("To refit, align the plug in its socket and press down until the brim seats. Press the cover evenly onto the brim.", RIGHT, 329.0, RW)
            .size(12.0, 17.0)
            .limit(51.0),
    )?;
    b.caption(
        "Filter: replace yearly; relieve the white line's pressure as on page 31 first. Cylinder: refill when its left gauge reaches the red band. Keep the spare nylon washer for the refill.",
        402.0,
        M,
        CW,
    )?;
    b.end()?;

    // Interior 31
    b.header("Check a leaking water connection", "FIRST CHECKS", None, None)?;
    b.note("FIRST, CLOSE THE SUPPLIES", "Close the water shutoff and cylinder valve. Unplug the machine. Leave pressurized connections assembled.", 139.0, M, CW, false)?;
    b.text("White TAP line", M, 260.0, 17.0, Face::Bold, NAVY)?;
    b.para(
        Para::new("Run the tap or dispenser on that same cold-water line until flow stops. Keep the white tee's side lever open, if used.", M, 292.0, 263.0)
            .size(12.0, 17.0)
            .limit(85.0),
    )?;
    b.text("Blue SODA line", M, 365.0, 17.0, Face::Bold, NAVY)?;
    b.para(Para::new("Press the soda lever over a jug until water and hissing stop.", M, 397.0, 263.0).size(12.0, 17.0).limit(34.0))?;
    b.text("After pressure is released", RIGHT, 260.0, 17.0, Face::Bold, NAVY)?;
    b.para(
        Para::new(
            "Hold the release ring in with the collet press. Pull out the tube and check for dirt or damage. Push an undamaged tube fully to its internal stop, then tug gently.",
            RIGHT,
            292.0,
            RW,
        )
        .size(12.0, 17.0)
        .limit(119.0),
    )?;
    b.end()?;

    // Interior 32
    b.header("Gas and first-pour checks", "FIRST CHECKS", None, None)?;
    b.text("Gas at a connection", M, 145.0, 17.0, Face::Bold, NAVY)?;
    b.para(Para::new("Close the cylinder valve. Growing bubbles in soapy water locate a leaking joint.", M, 180.0, 263.0).size(12.0, 16.0).limit(48.0))?;
    b.para(
        Para::new("<b>Leave the regulator and red tether assembled until depressurized.</b> Do not loosen a fitting to let pressure out.", M, 244.0, 263.0)
            .size(12.0, 16.0)
            .limit(64.0),
    )?;
    b.para(Para::new("Then check the nut's flat nylon washer and fully seat both red-tube ends. See pages 20-21.", M, 322.0, 263.0).size(12.0, 16.0).limit(64.0))?;
    b.para(Para::new("After repair, repeat the water and gas checks on pages 22-23 before connecting power.", M, 393.0, 263.0).size(12.0, 16.0).limit(48.0))?;
    for (y, title, s) in [
        (145.0, "No pour", "Check the water shutoff and the white tee's side-port lever."),
        (242.0, "No power", "Check the cord and outlet, then read any display message."),
        (339.0, "Warm pour", "Allow about an hour for the first chill."),
    ] {
        b.text(title, RIGHT, y, 17.0, Face::Bold, NAVY)?;
        b.para(Para::new(s, RIGHT, y + 32.0, RW).size(12.0, 17.0).limit(51.0))?;
    }
    b.end()?;

    back_cover(b)?;
    anyhow::ensure!(b.pages.len() == 34, "the booklet has {} pages", b.pages.len());
    Ok(())
}
