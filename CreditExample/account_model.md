
## PyMC model: produces samples of $\text{n{\textunderscore}at{\textunderscore}risk}$



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
\text{n{\textunderscore}at{\textunderscore}risk} &\sim \text{binomial}(\underline{\text{n{\textunderscore}accounts}}, \overline{\textbf{risk{\textunderscore}rate}}) \\
\text{n{\textunderscore}safe} &= \underline{\text{n{\textunderscore}accounts}} - \text{n{\textunderscore}at{\textunderscore}risk} \\
\end{align*}
$$

 * Function definitions:

$$
\begin{align*}
\text{pmf}(\textsf{ntp}, \textsf{nfp}) &\colonequals
  \text{binomial}(\text{n{\textunderscore}at{\textunderscore}risk}, \text{sensitivity}).\text{pmf}(\textsf{ntp}) \;\times\; \\
 &\; \text{binomial}(\text{n{\textunderscore}safe}, 1 - \text{specificity}).\text{pmf}(\textsf{nfp}) \\
\text{Z}() &\colonequals \sum_{\textsf{ntp} = 0}^{\overline{\textbf{n{\textunderscore}indications}}} \text{pmf}(\text{ntp}, \overline{\textbf{n{\textunderscore}indications}} - \textsf{ntp}) \\
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
\text{ntp} &\sim \text{pmf}(\textsf{ntp}, \overline{\textbf{n{\textunderscore}indications}} - \textsf{ntp}) / \ln(\text{Z}()) \\
\text{nfp} &= \overline{\textbf{n{\textunderscore}indications}} - \text{ntp} \\
\text{nfn} &= \text{n{\textunderscore}at{\textunderscore}risk} - \text{ntp} \\
\text{ntn} &= \text{n{\textunderscore}safe} - \text{nfp} \\
\end{align*}
$$

## Further sampled values

 * Attacker relations:

$$
\begin{align*}
\text{attacker{\textunderscore}coverage} \;\times\; \overline{\textbf{risk{\textunderscore}rate}} \sim \beta( &1 + \underline{\text{n{\textunderscore}compromised{\textunderscore}last{\textunderscore}year}}, \\
& 1 + \underline{\text{n{\textunderscore}accounts{\textunderscore}last{\textunderscore}year}} - \underline{\text{n{\textunderscore}compromised{\textunderscore}last{\textunderscore}year}}) \\
\end{align*}
$$

 * Result intermediates:

$$
\begin{align*}
\text{n{\textunderscore}failed{\textunderscore}treatment} &\sim \text{binomial}(\text{ntp}, 1 - \text{intervention{\textunderscore}effectiveness}) \\
\text{n additional compromised | no intervention} &\sim \text{binomial}(\text{ntp} - \text{n{\textunderscore}failed{\textunderscore}treatment}, \text{attacker{\textunderscore}coverage}) \\
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
\text{n compromised | intervention} &\sim \text{binomial}(\text{nfn} + \text{n{\textunderscore}failed{\textunderscore}treatment}, \text{attacker{\textunderscore}coverage}) \\
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

