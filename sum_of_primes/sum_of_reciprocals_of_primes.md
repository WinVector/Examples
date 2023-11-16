
<h2 id="Introduction">Introduction<a class="anchor-link" href="#Introduction"> </a></h2><p>In an <a href="https://win-vector.com/2023/11/13/yet-another-chatgpt-winge/">earlier note</a> I mentioned a specious attempt at a proof that the sum of the reciprocals of the prime integers diverges by ChatGPT3.5.</p>
<p>Let's take a moment and motivate and work through an actual correct proof. There is already an <a href="https://en.wikipedia.org/wiki/Divergence_of_the_sum_of_the_reciprocals_of_the_primes">excellent Wikipedia page on this</a>. However, I want to work this directly and slowly to show emphasize proof as test of ideas, and not of mere sequences of assertions.</p>
<p>Let's define our terms. A prime integer is a positive integer greater than 1 such that no <em>other</em> positive integer greater than 1 divides evenly into it. For a non-zero integer <code>x</code> and integer <code>y</code> we say "<code>x</code> divides evenly into <code>y</code>" if there is an integer <code>z</code> such that <code>y = x z</code>.</p>
<p>Let <code>p<sub>i</sub></code> denote the i-th prime integer.  The first few values are: <code>p<sub>1</sub> = 2</code>, <code>p<sub>2</sub> = 3</code>, <code>p<sub>3</sub> = 5</code>, <code>p<sub>4</sub> = 7</code>, and <code>p<sub>5</sub> = 11</code>.</p>
<p>We are going to prove that there are so many prime integers that <code>sum<sub>p: prime</sub> 1 / p</code> diverges. This implies there are not just an infinite number of primes- but that the size of the next prime number is not growing too fast.</p>


<h2 id="Setting-up-our-proof">Setting up our proof<a class="anchor-link" href="#Setting-up-our-proof"> </a></h2><p>Let's use Erd&#x0151;s's 1938 method to prove that <code>sum<sub>p: prime</sub> 1 / p</code> diverges.</p>
<p>We will use a proof by contradiction, and our set up is:</p>
<ul>
<li>Under the (to be falsified) assumption that <code>sum<sub>p: prime</sub> 1 / p</code> converges, pick
<code>s</code> so that <code>sum<sub>p: prime, p &gt; p<sub>s</sub></sub> 1 / p &lt; 1/4</code>. The idea is: for a sum of non-negative terms to converge, it must have arbitrarily small tail sums.</li>
<li>Pick <code>n = 2<sup>2 s + 6</sup></code>, and show how the integers in the range <code>[1, n]</code> are divided up under our assumption.</li>
</ul>
<p>Define are "small" primes as <code>p<sub>1</sub></code> through <code>p<sub>s</sub></code>, and the remaining primes (if any) as the large ones.</p>
<p>Erd&#x0151;s's idea is to break all integers in the range <code>[1, n]</code> into two classes:</p>
<ol>
<li><p>Integers in <code>[1, n]</code> not evenly divisible by any large prime. Call this set <code>S</code>.</p></li>
<li><p>Integers in <code>[1, n]</code> that are evenly divisible by at least one large prime. Call this set <code>T</code>.</p></li>
</ol>
<p>The plan is to exploit the relation <code>[1, n] = S union T</code>. We will show the set <code>T</code> is too small under our (to be falsified) assumption.</p>
<p>Most math proofs involving supposing a set of conditions that <em>if all shown</em> will complete the proof. Unfortunately, most sets of conditions don't actually work out. So mathematicians try many plausible combinations before they share a correct proof. This is to say: you shouldn't need to find the above compound outline convincing, the work of the proof is to confirm it. Also, things like <code>s</code> and <code>n</code> are picked by inspecting the end of earlier drafts of the proof.</p>
<p>Let's complete the proof.</p>


<h2 id="Finding-an-upper-bound-on-the-size-of-S">Finding an upper bound on the size of <code>S</code><a class="anchor-link" href="#Finding-an-upper-bound-on-the-size-of-S"> </a></h2><p>Any integer <code>z</code> in <code>S</code> can be written as:</p>
<p><code>z = m<sup>2</sup> p<sub>1</sub><sup>e<sub>1</sub></sup> ... p<sub>s</sub><sup>e<sub>s</sub></sup></code></p>
<p>where <code>m</code> is a positive integer in no larger than <code>sqrt(n)</code> (such that no large prime divides evenly into <code>m</code>) and each of the <code>e<sub>s</sub></code> are zero or one.</p>
<p>There are at most <code>(sqrt(n) + 1) 2<sup>s</sup></code> such numbers. So:</p>
<p><code>|S| &le; (sqrt(n) + 1) 2<sup>s</sup></code></p>
<p>The idea is: this probably isn't a large portion of <code>|[1, n]|</code>.</p>


<h2 id="Finding-a-(&quot;under-the-bubble-of-the-subjunctive&quot;)-upper-bound-on-the-size-of-T">Finding a ("under the bubble of the subjunctive") upper bound on the size of <code>T</code><a class="anchor-link" href="#Finding-a-(&quot;under-the-bubble-of-the-subjunctive&quot;)-upper-bound-on-the-size-of-T"> </a></h2><p>For a positive integer <code>z</code> we have <code>z</code> divides evenly into at most <code>1 + n / z</code> integers in the range <code>[1, n]</code>. We will use the crude bound that this itself is no more than <code>2 n / z</code>. Then the number of integers in the range <code>[1, n]</code> divisible by any of the large primes is no more than:</p>
<p><code></p>
<p><pre>
sum<sub>p: prime, p &gt; p<sub>s</sub></sub> 2 n / p
   = 2 n sum<sub>p: prime, p &gt; p<sub>s</sub></sub> 1 / p
   &lt; 2 n 1/4
   = n / 2
</pre>
</p>
<p>The replacement of <code>sum<sub>p: prime, p &gt; p<sub>s</sub></sub> 1 / p</code> with the bound <code>1/4</code> is where we are using the (to be falsified) assumption that <code>sum<sub>p: prime</sub> 1 / p</code> converges.</p>
<p>So, <em>if</em> <code>sum<sub>p: prime</sub> 1 / p</code> converges, then <code>|T| &lt; n/2</code>.</p>


<h2 id="Completing-the-proof">Completing the proof<a class="anchor-link" href="#Completing-the-proof"> </a></h2><p><code>[1, n] = S union T</code> so <code>|[1, n]| &le; |S| + |T|</code>. So we must have <code>n &le; |S| + |T|</code>. We will try to check, and find this fails.</p>
<p>If <code>sum<sub>p: prime</sub> 1 / p</code> converges, then our last equation implies:</p>
<p><code><pre>
n &le; (sqrt(n) + 1) 2<sup>s</sup> + n/2
</pre></code></p>
<p>Substitute our choice of <code>n = 2<sup>2 s + 6</sup></code> into the right hand side of the relation.</p>
<p><code><pre>
(sqrt(n) + 1) 2<sup>s</sup> + n/2
    = (sqrt(2<sup>2 s + 6</sup>) + 1) + 2<sup>2 s + 6</sup> / 2
    = (2<sup>s + 3</sup> + 1) + 2<sup>2 s + 5</sup> 
</pre></code></p>
<p>However, this is <em>smaller</em> than the left hand side <code>n</code>- not the required <em>at least as big</em>.</p>
<p>Therefore the assumption that <code>sum<sub>p: prime</sub> 1 / p</code> converges leads to contradiction, and we have shown <code>sum<sub>p: prime</sub> 1 / p</code> must in fact diverge.</p>


