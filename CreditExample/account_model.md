
## PyMC model: produces samples of n\_at\_risk



 * Scanner characteristics:

$$
\begin{align*}
\text{sensitivity} &\sim \beta(1 + \underline{\text{ctp}}, 1+ \underline{\text{cfn}}) \\
\text{specificity} &\sim \beta(1 + \underline{\text{ctn}}, 1+ \underline{\text{cfp}}) \\
\end{align*}
$$

 * Population characterisitics:

$$
\begin{align*}
\text{n\_at\_risk} &\sim \text{binomial}(\underline{\text{n\_accounts}}, \overline{\textbf{risk\_rate}}) \\
\text{n\_safe} &= \underline{\text{n\_accounts}} - \text{n\_at\_risk} \\
\end{align*}
$$

 * Function definitions:

$$
\begin{align*}
\text{pmf}(\textsf{ntp}, \textsf{nfp}) &\colonequals
  \text{binomial}(\text{n\_at\_risk}, \text{sensitivity}).\text{pmf}(\textsf{ntp}) \;\times\; \\
 &\; \text{binomial}(\text{n\_safe}, 1 - \text{specificity}).\text{pmf}(\textsf{nfp}) \\
\text{Z}() &\colonequals \sum_{\textsf{ntp} = 0}^{\overline{\textbf{n\_indications}}} \text{pmf}(\text{ntp}, \overline{\textbf{n\_indications}} - \textsf{ntp}) \\
\end{align*}
$$


 * Scan statistics:

$$
\begin{align*}
\text{Potential} &\; +\mkern-6mu= \ln(\text{Z}()) \\

\end{align*}
$$

## Confusion matrix terms

$$
\begin{align*}
\text{ntp} &\sim \text{pmf}(\textsf{ntp}, \overline{\textbf{n\_indications}} - \textsf{ntp}) / \ln(\text{Z}()) \\
\text{nfp} &= \overline{\textbf{n\_indications}} - \text{ntp} \\
\text{nfn} &= \text{n\_at\_risk} - \text{ntp} \\
\text{ntn} &= \text{n\_safe} - \text{nfp} \\
\end{align*}
$$

## Further sampled values

 * Attacker relations:

$$
\begin{align*}
\text{attacker\_coverage} \;\times\; \overline{\textbf{risk\_rate}} \sim \beta( &1 + \underline{\text{n\_compromised\_last\_year}}, \\
& 1 + \underline{\text{n\_accounts\_last\_year}} - \underline{\text{n\_compromised\_last\_year}}) \\
\end{align*}
$$

 * Result intermediates:

$$
\begin{align*}
\text{n\_failed\_treatment} &\sim \text{binomial}(\text{ntp}, 1 - \text{intervention\_effectiveness}) \\
\text{n additional compromised | no intervention} &\sim \text{binomial}(\text{ntp} - \text{n\_failed\_treatment}, \text{attacker\_coverage}) \\
\text{dollars additional compromised | no intervention} &\sim
\text{normal} \left(
    \begin{aligned}
    \mu &= \underline{\mu_{\text{loss}}}
    (\text{n additional compromised | no intervention}), \\
    \sigma &= \underline{\sigma_{\text{loss}}}
    \sqrt{\text{n additional compromised | no intervention}} \; 
        \end{aligned}
\right) \\
\end{align*}
$$

 * Outcomes:

$$
\begin{align*}
\text{n compromised | intervention} &\sim \text{binomial}(\text{nfn} + \text{n\_failed\_treatment}, \text{attacker\_coverage}) \\
\text{dollars compromised | intervention} &\sim 
\text{normal} \left(
    \begin{aligned}
    \mu &= \underline{\mu_{\text{loss}}}
    (\text{n compromised | intervention}), \\
    \sigma &= \underline{\sigma_{\text{loss}}}
    \sqrt{\text{n compromised | intervention}} \; 
        \end{aligned}
\right) \\
\text{n compromised | no intervention} &= (\text{n compromised | intervention}) + (\text{n additional compromised | no intervention}) \\
\text{dollars compromised | no intervention} &= (\text{dollars compromised | intervention}) + (\text{dollars additional compromised | no intervention}) \\
\end{align*}
$$

---

