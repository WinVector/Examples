package com.mzlabs.count;


/**
 * count A x = b x integral >= 0
 * @author johnmount
 *
 */
public class CountingProblem {
	public final int[][] A;
	
	public CountingProblem(final int[][] A) {
		this.A = A;
	}
	
	public IntVec normalForm(final IntVec b) {
		return b;
	}
}
