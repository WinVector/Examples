package com.mzlabs.fit;

public interface Link {
	/**
	 * 
	 * @param z
	 * @param res res.length==3, set to (f^{-1}(z),d/dz f^{-1}(z), d^2/dz^2 f^{-1}(z)
	 */
	void invLink(double z, double[] res);

	/**
	 * 
	 * @param z
	 * @return f^{-1}(z)
	 */
	double invLink(double z);
}
