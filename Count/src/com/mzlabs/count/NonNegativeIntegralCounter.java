package com.mzlabs.count;

import java.math.BigInteger;


public interface NonNegativeIntegralCounter {
	/**
	 * return the number of non-negative integer solutions to this(x) = b
	 * @param b non-negative integer vector
	 * @return
	 */
	public BigInteger countNonNegativeSolutions(final int[] b);
	
	/**
	 * Run a cheap check if the number of solutions is zero
	 * @param b
	 * @return true if obviously empty (always safe to return false)
	 */
	public boolean obviouslyEmpty(final int[] b);
}
