<h1>It isn't just the AIs hallucinating</h1>

`GPT-*` and the like are indeed amazing game-changing tools. However, they are not *currently* quite as magic as advertised.

As a minor example, consider the `popcount()` code example from [https://www.pcmag.com/news/samsung-software-engineers-busted-for-pasting-proprietary-code-into-chatgpt](https://www.pcmag.com/news/samsung-software-engineers-busted-for-pasting-proprietary-code-into-chatgpt).

When asked to correct the following code ChatGPT claims the fix is cleaning up some non-ascii characters *and* claims the code computes the number of bits set in the binary representation of the integer `n` (call this ideal quantity `popcount(n)`).

<img src="Screenshot 2023-05-02 at 8.22.26 AM.png">

Superficially this looks like some clever "popcount()" trick that "could get one hired based on Google's coding puzzles." One feels dumb for not knowing the apparently clever trick in the code.

However, believing that depends on not thinking about the code in terms of invariants. For the above code to work we would need to have the invariant that `count + popcount(n)` is a constant as we move through the loop. This would require the invariant that `n ^ (n - 1)` has one fewer bit set in the base-2 representation than `n` (as `count` increases by this much).

None of that is the case.

Consider working the example `n = 1`.


```python
n = 1
n ^ (n - 1)
```




    1



The code returns `1`, meaning the function will cycle- never returning any value. 

It appears some fraction of the magic of ChatGPT answers depends on not caring enough to read the answers carefully. The AIs work well in a world where nobody cares about the work. This is part of why they will in fact dominate writing tasks: nobody reads carefully.

It isn't just the AI's that are "hallucinating." Some of what they do is to form a **text-mirror** where the scorer is impressed by the training data and image of their own actions.

For those wondering, the usual trick is `n &= (n - 1)` (and, not xor). This works as it maps `2^k` to zero, which knocks the lowest `1` off the binary representation of `n`. So the example was likely attempting to solicit “replace `^` with `&`“.
