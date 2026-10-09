# Errors: the twelve misses and the exact lines

- ir-p01 lowercase const: found `const max_size`, want `const MAX_SIZE` in UPPERCASE.
- ir-p02 unwrap on Option: found `.unwrap()` on Option, want `match` with Some and None.
- ir-p03 unwrap on Result: found `.unwrap()` on Result, want `Result` with question mark.
- ir-p04 index loop: found `for i in 0..v.len()` with bracket read, want `iter()` with collect.
- ir-p05 mut setter: found `fn set_host` with mut ref, want builder `with_*` returning Self plus build.
- ir-p06 bare String id: found `id: String`, want newtype `UserId`.
- ir-p07 manual cleanup: found `fn cleanup` with no Drop, want RAII `impl Drop` with drop.
- ir-p08 missing trait: found free `fn extra` with no trait, want `trait Ext` plus blanket bound.
- ir-p09 owned str ref: found `&String`, want `&str`.
- ir-p10 owned clone: found `-> String` with clone and no Cow, want `Cow` borrowed or owned.
- ir-p11 clone in loop: found `for` with `.clone()`, want borrow `&item`.
- ir-p12 poly global: found `Deref` or `static mut` singleton or wide `unsafe`, want no Deref, no static mut, tiny unsafe with safety.

