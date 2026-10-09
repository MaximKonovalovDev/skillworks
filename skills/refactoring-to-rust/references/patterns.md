# Patterns: other-language game code into Rust

Each note below expands one rule of SKILL.md with the exact shape to write.
All snippets are original examples in the style of the source book. No book
text is copied here.

## C strings

A C function taking text receives a pointer to bytes ending in a zero byte.
Build that buffer with CString::new on the Rust side and read one back with
CStr::from_ptr inside a short unsafe block. Keep the CString alive while C
reads it: dropping it first leaves a dangling pointer.

```rust
let c_name = CString::new(name)?;
ffi::spawn_actor(c_name.as_ptr());
let back = unsafe { CStr::from_ptr(ffi::actor_name()) }.to_string_lossy();
```

## FFI boundary

Declare the foreign function with extern C and call it inside unsafe. Then
wrap both lines in a plain safe function the same day, so the rest of the
code never writes unsafe again.

```rust
extern "C" { fn solve(board: *const u8, len: usize) -> i32; }

fn solve_board(board: &[u8]) -> i32 {
    unsafe { solve(board.as_ptr(), board.len()) }
}
```

## Moves

Rust moves instead of copying. After let b = a the old name is gone; clone
it first with a.clone or borrow it with &a when the old name must stay alive.
Using the old name after the move stops the build with error E0382.

```rust
let b = a.clone();
draw(&a, b);
```

## Errors

C returns -1 and Python raises. In Rust both become Result with the question
mark operator on the happy path. Any function using the mark must return
Result or Option itself.

```rust
fn load(path: &str) -> Result<Level, LoadError> {
    let text = std::fs::read_to_string(path)?;
    Ok(Level::parse(&text)?)
}
```

## Python classes

A Python class with methods becomes a struct holding the fields plus an impl
block holding the methods. Where Python still calls in, expose the struct
through PyO3 with pyclass on the struct and pymethods on the impl block.

```rust
#[pyclass]
struct Fighter {
    hp: i32,
}

#[pymethods]
impl Fighter {
    fn damage(&mut self, amount: i32) {
        self.hp -= amount;
    }
}
```

## WASM async and JSON

A JS promise becomes an async fn exported through wasm-bindgen. JSON coming
back becomes a typed value through serde_json::from_str; on the WASM side
use serde-wasm-bindgen types so no hand-written glue is needed.

```rust
#[wasm_bindgen]
pub async fn fetch_level(url: &str) -> Result<JsValue, JsValue> {
    let text = download(url).await?;
    Ok(serde_wasm_bindgen::to_value(&Level::parse(&text)?)?)
}
```

## WASM build

Install the packer once with cargo install wasm-pack, then build with
wasm-pack build. Ship the pkg folder it writes. Never copy the glue files
by hand: a rebuild overwrites them and drifts from the source.

## Anything else

Snippets with no known marker still get a line in the report tagged OTHER.
The tag keeps the count honest: every line read is a line classified.

