package com.mzlabs.fit;

public interface Fitter {

	/**
	 * add a y ~ f(x) observation
	 * @param x
	 * @param y
	 * @param wt weight of observation (set to 1.0 in many cases)
	 */
	public abstract void addObservation(final double[] x, final double y,
			final double wt);

	public abstract double[] solve();

	/**
	 * 
	 * @param soln
	 * @param x length(soln)==length(x)+1
	 * @return
	 */
	public abstract double predict(final double[] soln, final double[] x);

}