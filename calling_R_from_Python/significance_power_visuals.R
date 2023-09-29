
library(wrapr)
library(ggplot2)
library(cdata)

# Assumes:
# * control is centered at zero
# * treatment centered at a positive number
# * both groups have the same variance
# 


sig_pow_visuals = function(
  stdev, 
  effect_size, 
  threshold, 
  title='Area under the tails give you significance and (1-power)',
  subtitle = 'Significance: control right tail; (1-Power): treatment left tail',
  eps=1e-6,
  control_color='#d95f02',
  treatment_color='#1b9e77') {
  x = c(threshold, threshold-eps, threshold+eps, seq(from=-5 * stdev, to=5 * stdev + effect_size, length.out=1000))
  x = sort(unique(x))
  control = dnorm(x, mean=0, sd = stdev)
  treatment = dnorm(x, mean=effect_size, sd=stdev)

  pframe = data.frame(x=x, control=control, treatment=treatment)
  # control's right tail
  pframe$control_tail = with(pframe, ifelse(x >= threshold, control, 0))
  # treatment's left tail
  pframe$treatment_tail = with(pframe, ifelse(x <= threshold, treatment, 0))

  controlTable = wrapr::qchar_frame(
    "group",      "y",        "tail" |
      "treatment",  treatment,  treatment_tail | 
      "control",    control,    control_tail
  )

  pframelong = rowrecs_to_blocks(pframe, 
                                 controlTable,
                                 columnsToCopy=c('x'))

  palette = c('control' = control_color, 'treatment' = treatment_color)

  p = ggplot(subset(pframelong, y > 1e-6), aes(x=x, y=y)) + 
    geom_line(aes(color=group)) + geom_vline(xintercept=threshold, color='gray50', linewidth=1) + 
    geom_ribbon(aes(ymin=0, ymax=tail, fill=group), alpha = 0.5) + 
    scale_color_manual(values=palette) + scale_fill_manual(values=palette) + 
    theme(legend.position='none') +
    ylab('density') + xlab('observed difference') + 
    ggtitle(title, subtitle=subtitle)

  p
}
