#[path = "_display_stock.rs"]
mod stock;

fn main() -> anyhow::Result<()> {
    stock::write()
}
