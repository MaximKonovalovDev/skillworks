# Patterns: the twelve Rustacean moves

Each pattern states the smell, the fix, and the token the checker branches on. All examples are fresh and tiny.

## Names

Name constants in UPPERCASE like MAX_SIZE, types in CamelCase like UserId, and functions plus variables in snake_case like user_id. A lowercase const or an uppercase function name fails the naming check. The rule keeps MAX_SIZE, UserId and user_id in their three cases.

## Option flow

Handle Option with match or if let over the Some and None arms. A call to unwrap on an Option panics on None and fails the check. The fixed arm keeps match with Some for the value and None for the fallback.

## Result flow

Return Result from fallible functions and propagate with the question mark operator. A call to unwrap on a Result in library code fails the check. The fixed function shows Result in its signature and the question mark at the call site.

## Iterators

Loop with iter plus map and collect instead of indexing with len and brackets. An index loop over 0 dot dot len with bracket reads fails the check. The fixed loop holds iter and collect with no index read.

## Builder

Chain with_* steps that take mut self and return Self, then close with build. A setter that takes a mut ref and returns unit fails the check. The fixed chain shows builder steps with Self and build at the end.

## Newtype

Wrap a bare String id in a newtype tuple struct like struct UserId with a String inside. A function that takes id as bare String fails the check. The fixed signature takes UserId and reads the inner field.

## RAII Drop

Tie cleanup to ownership with RAII by writing impl Drop for the guard type. A manual cleanup call with no Drop fails the check. The fixed type shows Drop with a drop method that runs the cleanup step.

## Extension and blanket

Add behavior with an extension trait named Ext and share it with a blanket impl over a bound. A free function that patches a foreign type with no trait fails the check. The fixed file shows trait Ext plus a blanket bound like Clone.

## Borrowed text

Take text as &str and slices as borrowed views, never as &String. A signature with &String fails the check. The fixed signature shows &str which accepts both owned and borrowed forms.

## Cow and mut

Default to immutable let bindings and hold maybe owned text in Cow. A function that takes String and clones it at once fails the check. The fixed signature shows Cow for the borrowed or owned branch with mut only where written.

## Clones

Clone only to move ownership across an API edge, never to feed a loop. A loop that clones each item fails the check. The fixed loop borrows with &item where the slow one called clone.

## Deref singletons unsafe

Never impl Deref to fake polymorphism, never hide state in a singleton with static mut, and keep unsafe tiny with a safety comment. A file with Deref or static mut or a wide unsafe block fails the check. The clean file shows no Deref, no static mut, and only a tiny unsafe block with a safety note.

