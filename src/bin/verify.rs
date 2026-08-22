//! Independent Rust Verifier for the PILL RED Protocol (PILLRED-SPEC-1.0).
//! Verifies Python-generated prediction receipts with zero server trust.

use pill_red_core::protocol::{verify_chain, verify_single, RawReceipt};
use std::env;
use std::fs;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    let file_path = if args.len() >= 2 {
        args[1].clone()
    } else {
        println!("============================================================");
        println!("         🔴 PILL RED ZERO-TRUST OFFLINE VERIFIER");
        println!("                     PILLRED-SPEC-1.0");
        println!("============================================================");
        println!("\nNo input file specified via command line arguments.");
        println!("\nPlease drag-and-drop a .json file (receipt, chain, or passport)");
        println!("into this window and press ENTER:");
        print!("> ");
        use std::io::Write;
        let _ = std::io::stdout().flush();
        let mut input = String::new();
        if std::io::stdin().read_line(&mut input).is_err() || input.trim().is_empty() {
            println!("[-] No file entered. Exiting.");
            wait_for_keypress();
            process::exit(1);
        }
        // Clean Windows drag-and-drop quotes
        input.trim().trim_matches('"').trim_matches('\'').to_string()
    };

    let content = match fs::read_to_string(&file_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("[-] Error reading file '{}': {}", file_path, e);
            wait_for_keypress();
            process::exit(1);
        }
    };

    let val: serde_json::Value = match serde_json::from_str(&content) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("[-] Error parsing JSON in '{}': {}", file_path, e);
            process::exit(1);
        }
    };

    let is_interactive = args.len() < 2;

    if val.is_object() && val.get("passport_hash").is_some() {
        println!("\n[*] 🔴 PILL RED Independent Rust Verifier (PILLRED-SPEC-1.0)");
        println!("[*] Auditing Model Audit Passport from: {}", file_path);
        println!("============================================================");
        match pill_red_core::protocol::verify_passport(&val) {
            Ok(_) => {
                println!("[✓] RUST PASSPORT AUDIT: PASSED (100% Intact)");
                println!("[*] Model ID:      {}", val.get("identity").and_then(|i| i.get("model_id")).unwrap_or(&serde_json::Value::Null));
                println!("[*] Passport Seal: {}", val.get("passport_hash").and_then(|p| p.as_str()).unwrap_or_default());
                if is_interactive { wait_for_keypress(); }
                process::exit(0);
            }
            Err(vios) => {
                println!("[✗] RUST PASSPORT AUDIT: FAILED! {} Violation(s) Found:", vios.len());
                for v in vios {
                    println!("    - {}", v);
                }
                if is_interactive { wait_for_keypress(); }
                process::exit(1);
            }
        }
    }

    let receipts: Vec<RawReceipt> = if val.is_array() {
        serde_json::from_value(val).expect("Failed to parse JSON array of receipts")
    } else {
        let single: RawReceipt = serde_json::from_value(val).expect("Failed to parse single JSON receipt");
        vec![single]
    };

    println!("\n[*] 🔴 PILL RED Independent Rust Verifier (PILLRED-SPEC-1.0)");
    println!("[*] Auditing {} receipt(s) from: {}", receipts.len(), file_path);
    println!("============================================================");

    for (idx, r) in receipts.iter().enumerate() {
        let status_res = verify_single(r);
        let hit_icon = if let Some(hit) = r.is_hit { if hit { "✓" } else { "✗" } } else { "🔒" };
        let prov_icon = if status_res.is_ok() { "✓" } else { "✗" };
        println!("[{}] [{}] Receipt #{:03} | ID: {} | Pred: {:?} | Outcome: {:?}", 
            hit_icon, prov_icon, idx + 1, r.receipt_id, r.prediction, r.actual_outcome);
    }

    println!("============================================================");
    match verify_chain(&receipts) {
        Ok(merkle_root) => {
            println!("[✓] RUST ZERO-TRUST AUDIT: PASSED (100% Provenance Intact)");
            println!("[*] Verified Merkle Root: {}", merkle_root);
            println!("[*] Temporal Precedence:  STRICTLY VERIFIED (t_commit < t_event <= t_resolve)");
            if is_interactive { wait_for_keypress(); }
            process::exit(0);
        }
        Err(violations) => {
            println!("[✗] RUST ZERO-TRUST AUDIT: FAILED! {} Violation(s) Found:", violations.len());
            for v in violations {
                println!("    - {}", v);
            }
            if is_interactive { wait_for_keypress(); }
            process::exit(1);
        }
    }
}

fn wait_for_keypress() {
    println!("\nPress ENTER to exit...");
    use std::io::Write;
    let _ = std::io::stdout().flush();
    let mut buf = String::new();
    let _ = std::io::stdin().read_line(&mut buf);
}

