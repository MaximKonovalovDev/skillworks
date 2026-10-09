# Scoped concurrency

Facts for engine work, distilled from the Programming Rust tour (chunks `0008.txt` and `0014.txt` to `0016.txt`). The same ownership rules that prevent memory errors also prevent data races.

Rust ties each mutex to the data it protects. Touch shared data only while holding the lock, which releases automatically when the guard drops. Read-only sharing across threads is checked the same way: the compiler refuses accidental mutation. Moving ownership of a structure to another thread relinquishes every sender-side access to it.

Scoped threads keep stack borrows safe. `std::thread::scope(|spawner| { ... })` waits for every spawned thread before it returns, so a thread may borrow a slice of a stack buffer without risking use after free. When the scope returns, the computation is complete.

Each thread needs exclusive access to its own piece. `pixels.chunks_mut(rows_per_band * bounds.0)` cuts the buffer into non-overlapping mutable bands, and `spawner.spawn(move || { ... })` moves one `band` slice into each thread. The `move` keyword takes ownership of the captured variables, so only the closure may use that band.

Size the pool from the machine with `std::thread::available_parallelism().expect(...).get()`, which yields a guaranteed-nonzero count. Round rows up with `div_ceil` so the bands cover the whole image even when the height is not a multiple of the thread count.

Measured with rustc 1.x (`rustc --edition 2021`):

```rust
fn render(band: &mut [u8], val: u8) {
    for b in band.iter_mut() {
        *b = val;
    }
}
fn main() {
    let mut pixels = vec![0u8; 12];
    let bands = pixels.chunks_mut(4);
    std::thread::scope(|spawner| {
        for (i, band) in bands.enumerate() {
            spawner.spawn(move || render(band, (i + 1) as u8));
        }
    });
    println!("{pixels:?}");
}
```

prints `[1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]`, exit 0. Each of the three bands was filled by its own thread, and the scope joined them all before printing.
