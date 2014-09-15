package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;

/**
 * TODO: test and confirm correctness of this class and use it to replace the taretSum>=0 function of OrderStepper
 * @author johnmount
 *
 */
final class OrderStepperTot extends FactorialBase implements Sequencer {
	public final int bound;
	public final int targetSum;
	
	/**
	 * walk through ordered x s.t. 0<=x<=b, sum(x)=targetSum
	 * @param dim >0
	 * @param bound >=0
	 * @param targetSum >=0
	 */
	public OrderStepperTot(final int dim, final int bound, final int targetSum) {
		super(dim);
		this.targetSum = targetSum;
		this.bound = Math.min(bound,targetSum);
		if(targetSum<0) {
			throw new IllegalArgumentException("total<0");
		}
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
		int leftSum = 0;
		for(int i=0;i<dim-1;++i) {
			leftSum += x[i];
		}
		int i = dim-1;
		do {
			final int xi = x[i];
			final int boundI = Math.min(bound,targetSum-(leftSum+(dim-i)*(xi+1)));
			if(boundI>=xi+1) {
				x[i] = xi+1;
				int sum = leftSum + x[i]; 
				for(int j=dim-1;j>i;--j) {
					final int allocation = Math.min(targetSum-sum,bound);
					x[j] = allocation;
					sum += allocation;
				}
				return true;
			}
			leftSum -= xi;
			--i;
		} while((i>=0)&&(leftSum>=0));
		return false;
	}
}
