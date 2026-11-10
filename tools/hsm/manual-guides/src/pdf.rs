//! PDF leaves retain their vector content and links when bound into a shop book.
use anyhow::{Context, Result, ensure};
use lopdf::{Bookmark, Dictionary, Document, Object, ObjectId, dictionary};
use std::path::Path;

fn inherited(doc: &Document, mut id: ObjectId, key: &[u8]) -> Result<Option<Object>> {
    loop {
        let node = doc.get_dictionary(id)?;
        if let Ok(value) = node.get(key) {
            return Ok(Some(doc.dereference(value)?.1.clone()));
        }
        let Ok(parent) = node.get(b"Parent").and_then(Object::as_reference) else {
            return Ok(None);
        };
        id = parent;
    }
}

pub fn merge(
    leaves: &[(std::path::PathBuf, String)],
    title: &str,
    contents_links: bool,
    target: &Path,
) -> Result<()> {
    let mut output = Document::with_version("1.7");
    let pages_id = output.new_object_id();
    let mut pages = Vec::new();
    for (path, _) in leaves {
        let mut leaf =
            Document::load(path).with_context(|| format!("read PDF leaf {}", path.display()))?;
        let ids: Vec<_> = leaf.get_pages().into_values().collect();
        ensure!(ids.len() == 1, "{} is not one printed leaf", path.display());
        let id = ids[0];
        let mut page = leaf.get_dictionary(id)?.clone();
        for key in [b"MediaBox".as_slice(), b"CropBox", b"Resources", b"Rotate"] {
            if let Some(value) = inherited(&leaf, id, key)? {
                page.set(key, value);
            }
        }
        leaf.objects.insert(id, Object::Dictionary(page));
        leaf.renumber_objects_with(output.max_id + 1);
        let id = *leaf
            .get_pages()
            .values()
            .next()
            .context("renumbered leaf page")?;
        leaf.get_dictionary_mut(id)?.set("Parent", pages_id);
        output.max_id = leaf.max_id;
        pages.push(id);
        output.objects.extend(leaf.objects);
    }
    let mut root = Dictionary::new();
    root.set("Type", "Pages");
    root.set("Count", pages.len() as i64);
    root.set(
        "Kids",
        pages
            .iter()
            .copied()
            .map(Object::Reference)
            .collect::<Vec<_>>(),
    );
    output.objects.insert(pages_id, Object::Dictionary(root));
    let catalog = output.add_object(
        dictionary! { "Type" => "Catalog", "Pages" => pages_id, "PageMode" => "UseOutlines" },
    );
    output.trailer.set("Root", catalog);
    for ((_, label), &page) in leaves.iter().zip(&pages) {
        output.add_bookmark(Bookmark::new(label.clone(), [0., 0., 0.], 0, page), None);
    }
    if contents_links && pages.len() > 1 {
        for (i, &page) in pages.iter().enumerate() {
            if i == 1 {
                continue;
            }
            let annotation = output.add_object(dictionary! {
                "Type" => "Annot", "Subtype" => "Link",
                "Rect" => vec![322.into(), 17.into(), 394.into(), 42.into()],
                "Border" => vec![0.into(), 0.into(), 0.into()],
                "Dest" => vec![Object::Reference(pages[1]), Object::Name(b"Fit".to_vec())],
            });
            let old = output.get_dictionary(page)?.get(b"Annots").ok().cloned();
            let mut annotations = match old {
                Some(value) => output.dereference(&value)?.1.as_array()?.clone(),
                None => Vec::new(),
            };
            annotations.push(Object::Reference(annotation));
            output.get_dictionary_mut(page)?.set("Annots", annotations);
        }
    }
    if let Some(outline) = output.build_outline() {
        output.catalog_mut()?.set("Outlines", outline);
    }
    let info = output.add_object(dictionary! {
        "Title" => Object::string_literal(title), "Author" => Object::string_literal("Home Soda Machine"),
        "Producer" => Object::string_literal("Home Soda Machine"), "Creator" => Object::string_literal(""),
    });
    output.trailer.set("Info", info);
    output.prune_objects();
    output.renumber_objects();
    output.compress();
    let mut bytes = Vec::new();
    output.save_to(&mut bytes)?;
    crate::write(target, &bytes)
}
