//! The install guide: the booklet's pages composed once, from its artwork, kit drawings and the
//! faucet's plate, and written as the reading copy the site shows, with the cover picture and
//! sidecar the Guides page lists it by. With `HSM_PRESS` set, as a print order needs, it also
//! writes Lulu's interior and outside-cover files and the bundle the order is placed from.
use anyhow::{Context, Result};
use std::path::Path;

#[path = "install-guide/book.rs"]
mod book;
#[path = "install-guide/pages.rs"]
mod pages;
#[path = "install-guide/press.rs"]
mod press;
#[path = "install-guide/slots.rs"]
mod slots;

fn write(path: &Path, bytes: &[u8]) -> Result<()> {
    std::fs::write(path, bytes).with_context(|| format!("writing {}", path.display()))
}

fn main() -> Result<()> {
    let root = std::path::absolute(".")?;
    let out = std::path::absolute(std::env::args().nth(1).unwrap_or_else(|| ".".into()))?;
    let mut book = book::Book::new(root)?;
    pages::compose(&mut book)?;

    let dir = out.join("hardware/install-guide");
    std::fs::create_dir_all(&dir)?;
    let reading = press::reading(&book)?;
    write(&dir.join("install-guide.pdf"), &reading)?;
    let cover = press::thumbnail(&book.pages[0]);
    write(&dir.join("install-guide.cover.png"), &cover.png()?)?;
    let sidecar = format!(
        "{{\n  \"title\": \"Home Soda Machine install guide\",\n  \"subtitle\": \"Owner install guide - seven steps in \
         detail - {interior} interior pages, 9 x 7 in landscape\",\n  \"pages\": {pages},\n  \"interior_pages\": {interior},\n  \
         \"cover\": \"install-guide.cover.png\",\n  \"cover_size\": [\n    {w},\n    {h}\n  ]\n}}\n",
        pages = book.pages.len(),
        interior = book.pages.len() - 2,
        w = cover.width,
        h = cover.height
    );
    write(&dir.join("install-guide.pdf.json"), sidecar.as_bytes())?;
    if std::env::var_os("HSM_PRESS").is_some() {
        press::order(&book, &reading, &out)?;
    }
    Ok(())
}
