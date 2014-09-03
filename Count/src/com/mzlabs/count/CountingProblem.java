package com.mzlabs.count;

import java.util.Arrays;

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
	
	public int[] normalForm(final int[] b) {
		return Arrays.copyOf(b,b.length);
	}
}
