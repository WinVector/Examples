package com.mzlabs.count.Minkowski;

import com.mzlabs.count.util.IntVec;

/**
 * step through all x s.t. x>=0 and sum(x)<=degree
 * @author johnmount
 *
 */
public final class SumStepper {
	public final int degree;
	
	public SumStepper(final int degree) {
		this.degree = degree;
	}

	public int[] first(final int dim) {
		return new int[dim];
	}
	
	public boolean next(final int[] x) {
		// find right-most advancible place
		int sum = 0;
		for(final int xi: x) {
			sum += xi;
		}
		final int n = x.length;
		int i = n-1;
		do {
			final int xi = x[i];
			if(sum+1<=degree) {
				x[i] = xi + 1;
				return true;
			}
			sum -= xi;
			x[i] = 0;
			--i;
		} while(i>=0);
		return false;
	}
	
	public static void main(String[] args) {
		// TODO: move to test
		final SumStepper stepper = new SumStepper(2);
		final int[] x = stepper.first(3);
		do {
			System.out.println(IntVec.toString(x));
		} while(stepper.next(x));
	}
}
