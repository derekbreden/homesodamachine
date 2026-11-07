//! The ledgers' readers and writers: the BOM's model masses, hardware counts and totals, the
//! attended labor, the print-farm occupancy, the purchase ledger and its evidence, as the ledger
//! programs (`hardware/ledger/*.rs`) and the document readers call them.
pub mod analysis;
pub mod bom;
pub mod bom_sync;
pub mod labor;
pub mod ledger_money;
pub mod ledger_totals;
pub mod printing;
pub mod shared;
