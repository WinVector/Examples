package com.mzlabs.count.op.iter;

import java.math.BigInteger;

import com.mzlabs.count.op.Sequencer;

public final class OrderStepper implements Sequencer {
	public final int dim;
	public final int bound;
	public final int targetSum;
	private final BigInteger[] factorial;
	
	/**
	 * 
	 * @param dim>0
	 * @param bound>=0
	 */
	public OrderStepper(final int dim, final int bound, final int targetSum) {
		this.dim = dim;
		this.targetSum = targetSum;
		if(targetSum>=0) {
			this.bound = Math.min(bound,targetSum);
		} else {
			this.bound = bound;
		}
		if((dim<=0)||(bound<0)) {
			throw new IllegalArgumentException("(" + dim + "," + bound + ")");
		}
		factorial = new BigInteger[Math.max(2,dim+1)];
		factorial[0] = BigInteger.ONE;
		factorial[1] = BigInteger.ONE;
		for(int i=2;i<=dim;++i) {
			factorial[i] = factorial[i-1].multiply(BigInteger.valueOf(i));
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
	 * @param x a sorted vector of integers of length dim
	 * @return number of distinct permutations of x
	 */
	public BigInteger nPerm(final int[] x) {
		BigInteger r = factorial[dim];
		int runLength = 1;
		for(int i=0;i<dim;++i) {
			if((i+1>=dim)||(x[i+1]!=x[i])) {
				if(runLength>1) {
					r = r.divide(factorial[runLength]);
				}
				runLength = 1;
			} else {
				runLength += 1;
			}
		}
		return r;
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
