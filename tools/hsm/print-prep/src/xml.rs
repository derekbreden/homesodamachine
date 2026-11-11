//! Enough XML to read back the members of a Bambu Studio project: elements, their attributes and
//! their text, without namespaces resolved (a name keeps its prefix).

use anyhow::{bail, Result};

#[derive(Debug, Default, Clone)]
pub struct Element {
    pub name: String,
    pub attributes: Vec<(String, String)>,
    pub children: Vec<Element>,
    pub text: String,
}

impl Element {
    pub fn attribute(&self, key: &str) -> Option<&str> {
        self.attributes.iter().find(|(k, _)| k == key).map(|(_, v)| v.as_str())
    }

    /// The local name, after any namespace prefix.
    pub fn local(&self) -> &str {
        self.name.rsplit(':').next().unwrap_or(&self.name)
    }

    pub fn child(&self, local: &str) -> Option<&Element> {
        self.children.iter().find(|c| c.local() == local)
    }

    pub fn children_named<'a>(&'a self, local: &'a str) -> impl Iterator<Item = &'a Element> + 'a {
        self.children.iter().filter(move |c| c.local() == local)
    }

    /// Every element below this one, depth first.
    pub fn descendants(&self) -> Vec<&Element> {
        let mut out = Vec::new();
        let mut stack: Vec<&Element> = self.children.iter().rev().collect();
        while let Some(e) = stack.pop() {
            out.push(e);
            stack.extend(e.children.iter().rev());
        }
        out
    }
}

/// Write the XML member of a Bambu project or sliced plate.
pub fn document(element: &Element) -> Vec<u8> {
    let mut out = String::from("<?xml version='1.0' encoding='utf-8'?>\n");
    serialize(element, &mut out);
    out.into_bytes()
}

fn serialize(element: &Element, out: &mut String) {
    fn escape(text: &str) -> String {
        text.replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
            .replace('"', "&quot;")
    }
    out.push('<');
    out.push_str(&element.name);
    for (key, value) in &element.attributes {
        out.push(' ');
        out.push_str(key);
        out.push_str("=\"");
        out.push_str(&escape(value));
        out.push('"');
    }
    if element.children.is_empty() && element.text.is_empty() {
        out.push_str(" />");
        return;
    }
    out.push('>');
    out.push_str(&escape(&element.text));
    for child in &element.children {
        serialize(child, out);
    }
    out.push_str("</");
    out.push_str(&element.name);
    out.push('>');
}

fn unescape(text: &str) -> String {
    if !text.contains('&') {
        return text.to_string();
    }
    let mut out = String::with_capacity(text.len());
    let mut rest = text;
    while let Some(at) = rest.find('&') {
        out.push_str(&rest[..at]);
        let tail = &rest[at..];
        let Some(end) = tail.find(';') else {
            out.push_str(tail);
            return out;
        };
        let entity = &tail[1..end];
        match entity {
            "amp" => out.push('&'),
            "lt" => out.push('<'),
            "gt" => out.push('>'),
            "quot" => out.push('"'),
            "apos" => out.push('\''),
            _ if entity.starts_with("#x") => out.extend(u32::from_str_radix(&entity[2..], 16).ok().and_then(char::from_u32)),
            _ if entity.starts_with('#') => out.extend(entity[1..].parse::<u32>().ok().and_then(char::from_u32)),
            _ => out.push_str(&tail[..=end]),
        }
        rest = &tail[end + 1..];
    }
    out.push_str(rest);
    out
}

fn attributes(text: &str) -> Result<Vec<(String, String)>> {
    let mut out = Vec::new();
    let mut rest = text.trim();
    while !rest.is_empty() {
        let Some(eq) = rest.find('=') else { bail!("an attribute without a value in <{text}>") };
        let key = rest[..eq].trim().to_string();
        let after = rest[eq + 1..].trim_start();
        let quote = after.chars().next().filter(|c| *c == '"' || *c == '\'');
        let Some(quote) = quote else { bail!("an unquoted attribute in <{text}>") };
        let Some(close) = after[1..].find(quote) else { bail!("an unclosed attribute in <{text}>") };
        out.push((key, unescape(&after[1..1 + close])));
        rest = after[close + 2..].trim_start();
    }
    Ok(out)
}

/// The document's root element.
pub fn parse(text: &str) -> Result<Element> {
    let mut stack: Vec<Element> = vec![Element::default()];
    let mut at = 0;
    let bytes = text.as_bytes();
    while at < bytes.len() {
        let Some(open) = text[at..].find('<').map(|i| at + i) else {
            stack.last_mut().unwrap().text.push_str(&unescape(&text[at..]));
            break;
        };
        if open > at {
            stack.last_mut().unwrap().text.push_str(&unescape(&text[at..open]));
        }
        let rest = &text[open..];
        if rest.starts_with("<?") {
            at = open + rest.find("?>").map_or(rest.len(), |i| i + 2);
        } else if rest.starts_with("<!--") {
            at = open + rest.find("-->").map_or(rest.len(), |i| i + 3);
        } else if rest.starts_with("<![CDATA[") {
            let end = rest.find("]]>").unwrap_or(rest.len());
            stack.last_mut().unwrap().text.push_str(&rest[9..end]);
            at = open + end + 3;
        } else if rest.starts_with("<!") {
            at = open + rest.find('>').map_or(rest.len(), |i| i + 1);
        } else if let Some(name) = rest.strip_prefix("</") {
            let close = name.find('>').unwrap_or(name.len());
            let done = stack.pop().unwrap();
            if done.name != name[..close].trim() {
                bail!("</{}> closes <{}>", name[..close].trim(), done.name);
            }
            stack.last_mut().unwrap().children.push(done);
            at = open + 2 + close + 1;
        } else {
            let close = rest.find('>').unwrap_or(rest.len());
            let inner = &rest[1..close];
            let empty = inner.ends_with('/');
            let inner = inner.trim_end_matches('/');
            let split = inner.find(char::is_whitespace).unwrap_or(inner.len());
            let element = Element { name: inner[..split].to_string(), attributes: attributes(&inner[split..])?, ..Default::default() };
            if empty {
                stack.last_mut().unwrap().children.push(element);
            } else {
                stack.push(element);
            }
            at = open + close + 1;
        }
    }
    if stack.len() != 1 {
        bail!("<{}> is not closed", stack.last().unwrap().name);
    }
    stack.pop().unwrap().children.into_iter().next().ok_or_else(|| anyhow::anyhow!("no root element"))
}

#[cfg(test)]
mod tests {
    #[test]
    fn reads_elements_attributes_and_text() {
        let root = super::parse("<?xml version='1.0'?><a x=\"1 &amp; 2\"><b y='z'/><c>t&lt;u</c></a>").unwrap();
        assert_eq!(root.attribute("x"), Some("1 & 2"));
        assert_eq!(root.child("b").unwrap().attribute("y"), Some("z"));
        assert_eq!(root.child("c").unwrap().text, "t<u");
    }
}
