package com.mzlabs.count.op.iter;

import java.math.BigInteger;

import com.mzlabs.count.op.Sequencer;

public final class OrderStepper extends FactorialBase implements Sequencer  {
	public final int bound;
	public final int targetSum;

	/**
	 * 
	 * @param dim >0
	 * @param bound >=0
	 */
	public OrderStepper(final int dim, final int bound, final int targetSum) {
		super(dim);
		this.targetSum = targetSum;
		if(bound<0) {
			throw new IllegalArgumentException("bound<0");
		}
		if(targetSum>=0) {
			this.bound = Math.min(bound,targetSum);
		} else {
			this.bound = bound;
		}
		if((dim<=0)||(bound<0)) {
			throw new IllegalArgumentException("(" + dim + "," + bound + ")");
		}
	}
	
	
	/**
	 * 
	 * @param targetSum if >0 check if there is valid start
	 * @return
	 */
	@Override
	public int[] first() {
		int[] x = new int[dim];
		if(targetSum>=0) {
			int remaining = targetSum;
			int i = dim-1;
			while((i>=0)&&(remaining>0)) {
				final int allocation = Math.min(remaining,bound);
				x[i] = allocation;
				remaining -= allocation;
				--i;
			}
			if(remaining>0) {
				x = null;
			}
			return x;
		} else {
			return x;
		}
	}
	
	/**
	 * step through all x s.t. 0<=x<=b and x[i+1]>=x[i]
	 * @param bounds
	 * @param x start at all zeros
	 * @return true if valid vector
	 */
	private boolean advanceLEI(final int[] x) {
		// find right-most advanceble position
		int i = dim-1;
		do {
			if(x[i]<bound) {
				final int nv = x[i]+1;
				for(int j=i;j<dim;++j) {
					x[j] = nv;
				}
				return true;
			}
			--i;
		} while(i>=0);
		return false;
	}
	
	
	// TODO: efficient implementation of this (right-fill in rule is different)
	private boolean advanceLEIs(final int[] x) {
		while(true) {
			if(!advanceLEI(x)) {
				return false;
			}
			int sum = 0;
			for(final int xi: x) {
				sum += xi;
			}
			if(targetSum==sum) {
				return true;
			}
		}
	}
	
	@Override
	public boolean advance(int[] x) {
		if(targetSum<0) {
			return advanceLEI(x);
		} else {
			return advanceLEIs(x);
		}
	}
	

	/**
	 * should have sum_{advance(x)} nPerm(x) = (bound+1)^dim
	 * 
	 */
	public boolean checks() {
		final int[] x = first();
		BigInteger sum = BigInteger.ZERO;
		do {
			final BigInteger nperm = nPerm(x);
			//System.out.println(Arrays.toString(x) + "\t" + nperm);
			sum = sum.add(nperm);
		} while(advanceLEI(x));
		final BigInteger check = BigInteger.valueOf(bound+1).pow(dim);
		return check.compareTo(sum)==0;
	}
}
