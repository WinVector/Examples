
## PyMC model: produces samples of $\text{n{\textendash}at{\textendash}risk}$



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
\text{n{\textendash}at{\textendash}risk} &\sim \text{binomial}(\underline{\text{n{\textendash}accounts}}, \overline{\textbf{risk{\textendash}rate}}) \\
\text{n{\textendash}safe} &= \underline{\text{n{\textendash}accounts}} - \text{n{\textendash}at{\textendash}risk} \\
\end{align*}
$$

 * Function definitions:

$$
\begin{align*}
\text{pmf}(\textsf{ntp}, \textsf{nfp}) &\colonequals
  \text{binomial}(\text{n{\textendash}at{\textendash}risk}, \text{sensitivity}).\text{pmf}(\textsf{ntp}) \;\times\; \\
 &\; \text{binomial}(\text{n{\textendash}safe}, 1 - \text{specificity}).\text{pmf}(\textsf{nfp}) \\
\text{Z}() &\colonequals \sum_{\textsf{ntp} = 0}^{\overline{\textbf{n{\textendash}indications}}} \text{pmf}(\text{ntp}, \overline{\textbf{n{\textendash}indications}} - \textsf{ntp}) \\
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
\text{ntp} &\sim \text{pmf}(\textsf{ntp}, \overline{\textbf{n{\textendash}indications}} - \textsf{ntp}) / \ln(\text{Z}()) \\
\text{nfp} &= \overline{\textbf{n{\textendash}indications}} - \text{ntp} \\
\text{nfn} &= \text{n{\textendash}at{\textendash}risk} - \text{ntp} \\
\text{ntn} &= \text{n{\textendash}safe} - \text{nfp} \\
\end{align*}
$$

## Further sampled values

 * Attacker relations:

$$
\begin{align*}
\text{attacker{\textendash}coverage} \;\times\; \overline{\textbf{risk{\textendash}rate}} \sim \beta( &1 + \underline{\text{n{\textendash}compromised{\textendash}last{\textendash}year}}, \\
& 1 + \underline{\text{n{\textendash}accounts{\textendash}last{\textendash}year}} - \underline{\text{n{\textendash}compromised{\textendash}last{\textendash}year}}) \\
\end{align*}
$$

 * Result intermediates:

$$
\begin{align*}
\text{n{\textendash}failed{\textendash}treatment} &\sim \text{binomial}(\text{ntp}, 1 - \text{intervention{\textendash}effectiveness}) \\
\text{n additional compromised | no intervention} &\sim \text{binomial}(\text{ntp} - \text{n{\textendash}failed{\textendash}treatment}, \text{attacker{\textendash}coverage}) \\
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
\text{n compromised | intervention} &\sim \text{binomial}(\text{nfn} + \text{n{\textendash}failed{\textendash}treatment}, \text{attacker{\textendash}coverage}) \\
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

