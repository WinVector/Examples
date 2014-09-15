package com.mzlabs.count.op.iter;

import java.math.BigInteger;

import com.mzlabs.count.op.Sequencer;

public final class OrderStepper extends FactorialBase implements Sequencer  {
	public final int bound;

	/**
	 * 
	 * @param dim >0
	 * @param bound >=0
	 */
	public OrderStepper(final int dim, final int bound) {
		super(dim);
		this.bound = bound;
		if(bound<0) {
			throw new IllegalArgumentException("bound<0");
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
		return x;
	}
	
	/**
	 * step through all x s.t. 0<=x<=b and x[i+1]>=x[i]
	 * @param bounds
	 * @param x start at all zeros
	 * @return true if valid vector
	 */
	@Override
	public boolean advance(final int[] x) {
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
			int lastXi = 0;
			for(final int xi: x) {
				if((xi<0)||(xi>bound)||(xi<lastXi)) {
					return false;
				}
				lastXi = xi;
			}
			sum = sum.add(nperm);
		} while(advance(x));
		final BigInteger check = BigInteger.valueOf(bound+1).pow(dim);
		return check.compareTo(sum)==0;
	}
}
