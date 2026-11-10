//! The requested refrigerant proof draws the maintained warning text as measured font outlines.
use anyhow::{Context, Result, bail, ensure};
use hsm_pages::{Font, Page, Path as Drawing, Pen, Rgb, Seg, pdf};
use lopdf::{Object, dictionary};
use serde_json::json;
use std::{fmt::Write as _, path::Path};

const MM: f64 = 72. / 25.4;
const LETTER: [f64; 2] = [612., 792.];
const CAP: f64 = 6.5;
const WIDTH: f64 = 190.;
const MARGIN: f64 = 6.;
const LEADING: f64 = 9.;
const SYMBOL_HEIGHT: f64 = 18.;
const SYMBOL_SOURCE_HEIGHT: f64 = 523.6;
const INK: Rgb = Rgb::hex("#161616");
const BLACK: Rgb = Rgb::hex("#000000");

struct Outline {
    path: Drawing,
    bounds: [f64; 4],
}
impl Outline {
    fn width(&self) -> f64 { self.bounds[2] - self.bounds[0] }
    fn height(&self) -> f64 { self.bounds[3] - self.bounds[1] }
    fn offset(&self, x: f64, y: f64) -> [f64; 2] { [x - self.bounds[0], y - self.bounds[1]] }
}

fn glyph(font: &Font, c: char) -> Result<tiny_skia::Path> {
    let mut builder = tiny_skia::PathBuilder::new();
    font.outline(font.glyph(c), 1., [0., 0.], &mut builder);
    builder.finish().with_context(|| format!("warning glyph {c:?} has no outline"))
}

fn text_outline(font: &Font, value: &str, cap: f64) -> Result<Outline> {
    let cap_height = glyph(font, 'H')?.compute_tight_bounds().context("H bounds")?.height() as f64;
    let em = cap / cap_height;
    let mut advance = 0.;
    let mut path = Drawing::new();
    let mut bounds = [f64::INFINITY, f64::INFINITY, f64::NEG_INFINITY, f64::NEG_INFINITY];
    for c in value.chars() {
        if !c.is_whitespace() {
            let source = glyph(font, c)?;
            let b = source.compute_tight_bounds().context("glyph bounds")?;
            bounds[0] = bounds[0].min(advance + b.left() as f64 * em);
            bounds[1] = bounds[1].min(-b.bottom() as f64 * em);
            bounds[2] = bounds[2].max(advance + b.right() as f64 * em);
            bounds[3] = bounds[3].max(-b.top() as f64 * em);
            let at = |p: tiny_skia::Point| [advance + p.x as f64 * em, -p.y as f64 * em];
            let mut current = [0., 0.];
            for segment in source.segments() {
                use tiny_skia::PathSegment::*;
                match segment {
                    MoveTo(p) => { current = at(p); path.move_to(current[0], current[1]); }
                    LineTo(p) => { current = at(p); path.line_to(current[0], current[1]); }
                    QuadTo(q, p) => {
                        let (q, p) = (at(q), at(p));
                        path.curve_to(
                            [current[0] + (q[0]-current[0])*2./3., current[1] + (q[1]-current[1])*2./3.],
                            [p[0] + (q[0]-p[0])*2./3., p[1] + (q[1]-p[1])*2./3.], p);
                        current = p;
                    }
                    CubicTo(a, b, p) => { current = at(p); path.curve_to(at(a), at(b), current); }
                    Close => { path.close(); }
                }
            }
        }
        advance += font.advance(font.glyph(c)) * em / 1000.;
    }
    ensure!(bounds.iter().all(|v| v.is_finite()), "empty warning text");
    Ok(Outline { path, bounds })
}

fn transform(path: &Drawing, matrix: [f64; 6]) -> Drawing {
    let at = |p: [f64; 2]| [matrix[0]*p[0]+matrix[2]*p[1]+matrix[4], matrix[1]*p[0]+matrix[3]*p[1]+matrix[5]];
    Drawing { segs: path.segs.iter().map(|segment| match *segment {
        Seg::Move(p) => Seg::Move(at(p)), Seg::Line(p) => Seg::Line(at(p)),
        Seg::Cubic(a,b,p) => Seg::Cubic(at(a),at(b),at(p)), Seg::Close => Seg::Close,
    }).collect() }
}
fn pdf_path(path: &Drawing, x: f64, top: f64) -> Drawing {
    transform(path, [MM,0.,0.,-MM,x*MM,LETTER[1]-top*MM])
}
fn svg_path(path: &Drawing) -> String {
    let mut value = String::new();
    for seg in &path.segs {
        match seg {
            Seg::Move(p) => { let _=write!(value,"M{} {}",p[0],p[1]); }
            Seg::Line(p) => { let _=write!(value,"L{} {}",p[0],p[1]); }
            Seg::Cubic(a,b,p) => { let _=write!(value,"C{} {} {} {} {} {}",a[0],a[1],b[0],b[1],p[0],p[1]); }
            Seg::Close => value.push('Z'),
        }
    }
    value
}
fn escaped(value: &str) -> String {
    value.replace('&',"&amp;").replace('<',"&lt;").replace('>',"&gt;").replace('"',"&quot;").replace('\'',"&#x27;")
}

struct Numbers<'a> { value: &'a [u8], at: usize }
impl<'a> Numbers<'a> {
    fn new(value: &'a str) -> Self { Self { value:value.as_bytes(),at:0 } }
    fn skip(&mut self) { while self.at<self.value.len()&&(self.value[self.at].is_ascii_whitespace()||self.value[self.at]==b',') {self.at+=1;} }
    fn number(&mut self) -> Result<f64> {
        self.skip(); let start=self.at;
        if self.at<self.value.len()&&matches!(self.value[self.at],b'+'|b'-') {self.at+=1;}
        while self.at<self.value.len()&&(self.value[self.at].is_ascii_digit()||self.value[self.at]==b'.') {self.at+=1;}
        if self.at<self.value.len()&&matches!(self.value[self.at],b'e'|b'E') {
            self.at+=1;
            if self.at<self.value.len()&&matches!(self.value[self.at],b'+'|b'-') {self.at+=1;}
            while self.at<self.value.len()&&self.value[self.at].is_ascii_digit() {self.at+=1;}
        }
        ensure!(self.at>start,"expected SVG coordinate");
        Ok(std::str::from_utf8(&self.value[start..self.at])?.parse()?)
    }
    fn pair(&mut self) -> Result<[f64;2]> { Ok([self.number()?,self.number()?]) }
}

fn parse_path(value: &str) -> Result<Drawing> {
    let mut reader=Numbers::new(value); let mut command=b' '; let mut current=[0.,0.]; let mut start=current; let mut path=Drawing::new();
    loop {
        reader.skip(); if reader.at==reader.value.len() {break;}
        if reader.value[reader.at].is_ascii_alphabetic() {command=reader.value[reader.at];reader.at+=1;}
        let relative=command.is_ascii_lowercase();
        let point=|p:[f64;2]| if relative {[p[0]+current[0],p[1]+current[1]]} else {p};
        match command.to_ascii_uppercase() {
            b'M' => {current=point(reader.pair()?);start=current;path.move_to(current[0],current[1]);command=if relative {b'l'} else {b'L'};}
            b'L' => {current=point(reader.pair()?);path.line_to(current[0],current[1]);}
            b'H' => {let x=reader.number()?;current[0]=if relative {current[0]+x} else {x};path.line_to(current[0],current[1]);}
            b'V' => {let y=reader.number()?;current[1]=if relative {current[1]+y} else {y};path.line_to(current[0],current[1]);}
            b'C' => {let a=point(reader.pair()?);let b=point(reader.pair()?);let p=point(reader.pair()?);path.curve_to(a,b,p);current=p;}
            b'Z' => {path.close();current=start;command=b' ';}
            other => bail!("unsupported W021 SVG path command {}",other as char),
        }
    }
    Ok(path)
}
fn attribute<'a>(tag: &'a str, name: &str) -> Option<&'a str> {
    let marker=format!("{name}=\""); let start=tag.find(&marker)?+marker.len(); let tail=&tag[start..]; Some(&tail[..tail.find('"')?])
}
struct Symbol { svg:String, shapes:Vec<(Drawing,Rgb)> }
impl Symbol {
    fn read(file: &Path) -> Result<Self> {
        let value=std::fs::read_to_string(file)?; let mut svg=String::new();let mut shapes=Vec::new();
        let mut rest=value.as_str();
        while let Some(start)=rest.find('<') {
            rest=&rest[start..]; let end=rest.find('>').context("W021 tag")?+1;let tag=&rest[..end];rest=&rest[end..];
            if !(tag.starts_with("<path ")||tag.starts_with("<path\n")||tag.starts_with("<polygon ")||tag.starts_with("<polygon\n")) {continue;}
            svg.push_str(tag);
            let mut path=if tag.starts_with("<path") {parse_path(attribute(tag,"d").context("W021 path data")?)?} else {
                let mut numbers=Numbers::new(attribute(tag,"points").context("W021 polygon points")?);let mut points=Vec::new();
                loop {numbers.skip();if numbers.at==numbers.value.len(){break;}points.push(numbers.pair()?);}
                Drawing::polyline(&points,true)
            };
            if let Some(matrix)=attribute(tag,"transform") {
                let matrix=matrix.strip_prefix("matrix(").and_then(|v|v.strip_suffix(')')).context("W021 matrix transform")?;
                let mut n=Numbers::new(matrix);path=transform(&path,[n.number()?,n.number()?,n.number()?,n.number()?,n.number()?,n.number()?]);
            }
            let fill=attribute(tag,"style").and_then(|s|s.split(';').find_map(|p|p.strip_prefix("fill:"))).or_else(||attribute(tag,"fill")).unwrap_or("#000000");
            ensure!(fill.len()==7&&fill.starts_with('#'),"W021 fill color");shapes.push((path,Rgb::hex(fill)));
        }
        ensure!(shapes.len()==3,"W021 has its border, triangle and flame");Ok(Self {svg,shapes})
    }
}

struct Label {
    key:&'static str, title:&'static str, symbol:bool, lines:Vec<String>, height:f64,
    text:Vec<(String,f64,f64,f64)>,
}
impl Label {
    fn new(font:&Font,key:&'static str,title:&'static str,signal:&str,sentences:&[&str],symbol:bool) -> Result<Self> {
        let mut lines=Vec::new();
        for sentence in sentences {
            if sentence.contains('\n') {lines.extend(sentence.to_uppercase().lines().map(String::from));continue;}
            let mut current=String::new();
            for word in sentence.to_uppercase().split_whitespace() {
                let candidate=if current.is_empty(){word.into()}else{format!("{current} {word}")};
                if text_outline(font,&candidate,CAP)?.width()>WIDTH-2.*MARGIN {
                    ensure!(!current.is_empty(),"warning word exceeds label width");lines.push(current);current=word.into();
                } else {current=candidate;}
            }
            if !current.is_empty(){lines.push(current);}
        }
        let top=if symbol{33.}else{22.};let height=(top+(lines.len()-1) as f64*LEADING+CAP+MARGIN).ceil();
        let mut text=vec![(signal.into(),MARGIN,9.,9.)];
        if symbol{text.push(("R-600a".into(),137.,12.9,6.5));}
        text.extend(lines.iter().enumerate().map(|(i,line)|(line.clone(),MARGIN,top+i as f64*LEADING,CAP)));
        let label=Self {key,title,symbol,lines,height,text};label.audit(font)?;Ok(label)
    }
    fn minimum_height(&self,font:&Font) -> Result<f64> {
        self.lines.iter().flat_map(|l|l.chars()).filter(|c|c.is_alphabetic()).map(|c|Ok(text_outline(font,&c.to_string(),CAP)?.height())).collect::<Result<Vec<_>>>().map(|v|v.into_iter().fold(f64::INFINITY,f64::min))
    }
    fn audit(&self,font:&Font) -> Result<Vec<(String,f64,f64,f64,f64)>> {
        ensure!(self.minimum_height(font)?>=6.4,"warning letter height");let mut bounds=Vec::new();
        for (value,x,y,cap) in &self.text {
            let outline=text_outline(font,value,*cap)?;let(w,h)=(outline.width(),outline.height());
            ensure!(*x>=MARGIN&&x+w<=WIDTH-MARGIN,"warning line width: {value}");
            ensure!(*y>=MARGIN&&y+h<=self.height-MARGIN+0.2&&*cap>=6.4,"warning text bounds: {value}");
            bounds.push((value.clone(),*x,*y,w,h));
        }
        if self.symbol {bounds.push(("ISO 7010 W021".into(),108.,6.,600.*SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT,SYMBOL_HEIGHT));}
        for (i,a) in bounds.iter().enumerate(){for b in &bounds[i+1..]{ensure!(a.1+a.3<=b.1||b.1+b.3<=a.1||a.2+a.4<=b.2||b.2+b.4<=a.2,"{} overlapping elements: {} / {}",self.key,a.0,b.0);}}
        Ok(bounds)
    }
    fn svg(&self,font:&Font,symbol:&Symbol) -> Result<String> {
        let mut content=format!("<rect x=\"0.25\" y=\"0.25\" width=\"{}\" height=\"{}\" rx=\"2\" fill=\"white\" stroke=\"#161616\" stroke-width=\"0.5\"/>",WIDTH-0.5,self.height-0.5);
        for (value,x,y,cap) in &self.text {
            let outline=text_outline(font,value,*cap)?;let offset=outline.offset(*x,*y);
            write!(content,"<path aria-label=\"{}\" transform=\"translate({} {})\" d=\"{}\"/>",escaped(value),offset[0],offset[1],svg_path(&outline.path))?;
        }
        if self.symbol {write!(content,"<g transform=\"translate(108 6) scale({})\">{}</g>",SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT,symbol.svg)?;}
        Ok(format!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{WIDTH}mm\" height=\"{}mm\" viewBox=\"0 0 {WIDTH} {}\"><title>{}</title><desc>Household R-600a warning artwork. Uppercase body letters have a {CAP} mm H cap height. See README.md for applicability and installation status.</desc>{content}</svg>",self.height,self.height,self.title))
    }
    fn draw(&self,page:&mut Page,font:&Font,symbol:&Symbol,x:f64,top:f64) -> Result<()> {
        page.fill_stroke(pdf_path(&Drawing::round_rect(0.25,0.25,WIDTH-0.5,self.height-0.5,2.),x,top),Rgb::WHITE,Pen::new(INK,0.5*MM));
        for(value,tx,ty,cap)in &self.text {
            let outline=text_outline(font,value,*cap)?;let offset=outline.offset(*tx,*ty);
            page.fill(pdf_path(&transform(&outline.path,[1.,0.,0.,1.,offset[0],offset[1]]),x,top),BLACK);
        }
        if self.symbol {let k=SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT;for(path,fill)in &symbol.shapes{page.fill(pdf_path(&transform(path,[k,0.,0.,k,108.,6.]),x,top),*fill);}}
        Ok(())
    }
}

fn labels(font:&Font) -> Result<Vec<Label>> {
    Ok(vec![
        Label::new(font,"household-exterior-disposal","Exterior / disposal","CAUTION",&[
            "Risk of Fire Or Explosion.",
            "Dispose of Properly In Accordance With The Applicable Federal Or Local Regulations.",
            "Flammable Refrigerant Used.",
        ],false)?,
        Label::new(font,"household-service","Compressor compartment / service and tubing","DANGER",&[
            "Risk Of Fire Or Explosion Due To Puncture Of Refrigerant Tubing.",
            "Flammable Refrigerant Used.",
            "To Be Repaired Only By\nTrained Service Personnel.",
            "Do Not Puncture\nRefrigerant Tubing.",
            "Consult Repair Manual/Owner's Guide Before Attempting To Service This Product.",
            "All Safety Precautions\nMust Be Followed.",
            "Follow Handling Instructions Carefully.",
        ],true)?,
    ])
}

struct ProofText {font:&'static str,size:f64,x:f64,top:f64,text:String,fill:Rgb}
fn text(notes:&mut Vec<ProofText>,font:&'static str,size:f64,x:f64,top:f64,value:impl Into<String>,fill:Rgb){notes.push(ProofText{font,size,x,top,text:value.into(),fill});}
fn heading(notes:&mut Vec<ProofText>,page:usize,title:&str) {
    text(notes,"HB",14.,13.,16.,title,INK);
    text(notes,"H",9.,13.,23.,"FULL-SIZE FIT PROOF  /  US LETTER  /  PRINT AT 100%, ACTUAL SIZE",INK);
    text(notes,"H",8.,13.,LETTER[1]/MM-17.,"Household design specification. Paper is a fit template; use permanent production markings.",INK);
    text(notes,"H",8.,13.,LETTER[1]/MM-12.,"EPA Rule 22 / UL 60335-2-24 (April 28, 2017). Sources: hardware/markings/README.md.",INK);
    text(notes,"H",8.,203.-15.568/MM,LETTER[1]/MM-7.,format!("{page} / 2"),INK);
}
fn proof_label(page:&mut Page,notes:&mut Vec<ProofText>,label:&Label,font:&Font,symbol:&Symbol,top:f64)->Result<f64>{
    text(notes,"H",9.,13.,top,format!("{}  /  {WIDTH} x {} mm  /  6.5 mm body capitals",label.title,label.height),Rgb::hex("#555555"));
    label.draw(page,font,symbol,13.,top+4.)?;Ok(top+4.+label.height)
}
fn notes(out:&mut Vec<ProofText>,mut top:f64,lines:&[&str])->f64{for line in lines{text(out,"H",9.,13.,top,*line,Rgb::hex("#333333"));top+=5.;}top}
fn scale_bar(page:&mut Page,notes:&mut Vec<ProofText>,y:f64){
    for (a,b) in [([13.,y],[63.,y]),([13.,y-2.],[13.,y+2.]),([63.,y-2.],[63.,y+2.])]{page.stroke(pdf_path(&Drawing::polyline(&[a,b],false),0.,0.),Pen::new(INK,0.5));}
    text(notes,"H",9.,13.,y+7.,"50 mm at actual size. Do not use Fit or Shrink to page.",Rgb::hex("#333333"));
}
fn add_text(pdf:&mut lopdf::Document,page:lopdf::ObjectId,notes:&[ProofText],fonts:lopdf::Dictionary)->Result<()> {
    let resource=pdf.get_dictionary(page)?.get(b"Resources")?.clone();let mut resources=pdf.dereference(&resource)?.1.as_dict()?.clone();resources.set("Font",fonts);pdf.get_dictionary_mut(page)?.set("Resources",resources);
    let mut data=String::new();
    for note in notes {
        let value=note.text.replace('\\',"\\\\").replace('(',"\\(").replace(')',"\\)");
        writeln!(data,"BT /{} {} Tf {} {} {} rg {} {} Td ({value}) Tj ET",note.font,note.size,note.fill.r,note.fill.g,note.fill.b,note.x*MM,LETTER[1]-note.top*MM)?;
    }
    pdf.add_page_contents(page,data.into_bytes())?;Ok(())
}

pub fn build(root:&Path,output:Option<&Path>,font_file:Option<&Path>)->Result<()> {
    let source=root.join("hardware/markings");let dest=output.unwrap_or(root);
    let font_file=font_file.unwrap_or_else(||Path::new("/System/Library/Fonts/Helvetica.ttc"));
    let font=Font::from_collection("Helvetica-Bold",std::fs::read(font_file).with_context(||format!("read warning outline font {}",font_file.display()))?,1)?;
    let symbol=Symbol::read(&source.join("w021.svg"))?;let items=labels(&font)?;
    let mut pages=[Page::default(),Page::default()];let mut copy:[Vec<ProofText>;2]=Default::default();
    heading(&mut copy[0],1,"Household R-600a / exterior disposal warning");
    let bottom=proof_label(&mut pages[0],&mut copy[0],&items[0],&font,&symbol,34.)?;
    notes(&mut copy[0],bottom+12.,&[
        "Placement: on the outside of the enclosure; a rear or side face can carry this label.",
        "This warning does not need to occupy the brand / serial / QR nameplate.",
        "Wording: UL 60335-2-24 (2017), 7.1DV.4.1(d). Body capitals: at least 6.4 mm.",
        "",
        "Separate appliance information: manufacturer / model, voltage, AC frequency, rated current,",
        "manufacturing date or date code, R-600a, actual charge in grams, and foam blowing-agent ID.",
        "Use established unit values. The study text 5A / 600W is not a measured appliance rating.",
        "",
        "The disposal warning plus the service panel on page 2 cover the four applicable messages.",
        "The enclosed, foam-embedded evaporator has no user-contact defrost-warning location.",
        "No commercial storage paragraph, packaging paragraph, or A3 diamond is specified here.",
    ]);scale_bar(&mut pages[0],&mut copy[0],230.);
    heading(&mut copy[1],2,"Household R-600a / compressor compartment");
    let bottom=proof_label(&mut pages[1],&mut copy[1],&items[1],&font,&symbol,34.)?;
    let bottom=notes(&mut copy[1],bottom+10.,&[
        "Place near the compressor compartment and its exposed tubing, visible on gaining access.",
        "Combined equivalent wording for 7.1DV.4.1(b), (c), (e); all instructions retained.",
        "ISO 7010 W021 triangle: 18 mm high. R-600a identification visible at compressor access.",
        "Service-opening locations: PMS 185 red; process tube red at least 25 mm from compressor.",
    ]);ensure!(bottom<249.,"service proof notes fit the page");scale_bar(&mut pages[1],&mut copy[1],243.);
    let document=pdf::Document {sheets:pages.iter().map(|page|pdf::Sheet{page,size:LETTER,trim_inset:0.,offset:[0.,0.],links:false}).collect(),title:"Home Soda Machine - household R-600a warning fit proof".into(),author:"Derek Bredensteiner".into(),..Default::default()};
    let mut pdf=lopdf::Document::load_mem(&pdf::write(&document)?)?;
    let regular=pdf.add_object(dictionary!{"Type"=>"Font","Subtype"=>"Type1","BaseFont"=>"Helvetica","Encoding"=>"WinAnsiEncoding"});
    let bold=pdf.add_object(dictionary!{"Type"=>"Font","Subtype"=>"Type1","BaseFont"=>"Helvetica-Bold","Encoding"=>"WinAnsiEncoding"});
    for ((_,page),notes)in pdf.get_pages().into_iter().zip(&copy){add_text(&mut pdf,page,notes,dictionary!{"H"=>Object::Reference(regular),"HB"=>Object::Reference(bold)})?;}
    pdf.compress();let mut bytes=Vec::new();pdf.save_to(&mut bytes)?;
    let proof=dest.join("output/pdf/refrigerant-warning-proof.pdf");crate::write(&proof,&bytes)?;
    for item in &items {crate::write(&dest.join(format!("hardware/markings/artwork/{}.svg",item.key)),item.svg(&font,&symbol)?.as_bytes())?;}
    let minimum=items.iter().map(|item|item.minimum_height(&font)).collect::<Result<Vec<_>>>()?.into_iter().fold(f64::INFINITY,f64::min);
    let cap_height=glyph(&font,'H')?.compute_tight_bounds().context("H bounds")?.height() as f64;
    let audit=json!({
        "status":"household design specification; dimensioned fit proof; physical attachment not implemented",
        "standard":"UL 60335-2-24, second edition, April 28, 2017; EPA SNAP Rule 22",
        "warning_clauses":{"household-exterior-disposal":["7.1DV.4.1(d)"],"household-service":["7.1DV.4.1(b)","7.1DV.4.1(c)","7.1DV.4.1(e)"]},
        "service_wording":"Combined equivalent warning; DANGER heading and all substantive instructions retained",
        "body_cap_height_mm":CAP,"minimum_body_letter_ink_height_mm":(minimum*1e6).round()/1e6,"minimum_target_mm":6.4,
        "font":"Helvetica Bold, macOS Helvetica.ttc face 1; outlined","font_em_mm":(CAP/cap_height*1e6).round()/1e6,
        "symbol":"ISO 7010 W021","symbol_triangle_height_mm":SYMBOL_HEIGHT,
        "labels":items.iter().map(|item|Ok(json!({"file":format!("artwork/{}.svg",item.key),"width_mm":WIDTH,"height_mm":item.height,"body_lines":item.lines,"glyph_bounds":item.audit(&font)?}))).collect::<Result<Vec<_>>>()?,
    });crate::write_json(&dest.join("hardware/markings/artwork-dimensions.json"),&audit)?;
    println!("Refrigerant warning proof: two pages, outlined labels, measured bounds\n{}",proof.display());Ok(())
}
