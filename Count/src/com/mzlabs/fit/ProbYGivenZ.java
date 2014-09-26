package com.mzlabs.fit;

public interface ProbYGivenZ {
	/**
	 * 
	 * @param y
	 * @param z
	 * @param res res.length==3, set to (P(y|z),d/dz P(y|z), d^2/dz^2 P(y|z))
	 */
	void eval(double y, double z, double[] res);
}
