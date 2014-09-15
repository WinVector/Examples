package com.mzlabs.count.op.iter;

import java.util.SortedSet;
import java.util.TreeSet;

import com.mzlabs.count.op.Sequencer;
import com.mzlabs.count.util.IntVec;

/**
 * 
 * @author johnmount
 *
 */
public final class OrderStepperTot extends FactorialBase implements Sequencer {
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
			final int boundI = Math.min(bound,(targetSum-leftSum)/(dim-i));
			if(boundI>=xi+1) {
				final int ni = xi+1;
				x[i] = ni;
				int excessAllocation = targetSum - (leftSum+ (dim-i)*ni);
				for(int j=dim-1;j>i;--j) {
					final int xij = Math.min(bound,ni+excessAllocation);
					x[j] = xij;
					excessAllocation -= (xij-ni);
				}
				return true;
			}
			--i;
			if(i>=0) {
				leftSum -= x[i];
			}
		} while((i>=0)&&(leftSum>=0));
		return false;
	}
	
	public static boolean confirm(final int dim, final int bound, final int targetSum) {
		final SortedSet<IntVec> checkSet = new TreeSet<IntVec>();
		final OrderStepper checkStepper = new OrderStepper(dim,bound);
		//System.out.println("check " + dim + " " + bound + " " + targetSum);
		final int[] checkX = checkStepper.first();
		if(null!=checkX) {
			do {
				int sum = 0;
				for(final int xi: checkX) {
					sum += xi;
				}
				if(targetSum==sum) {
					final IntVec checkV = new IntVec(checkX);
					//System.out.println("\t" + checkV);
					checkSet.add(checkV);
				}
			} while(checkStepper.advance(checkX));
		}
		final OrderStepperTot stepper = new OrderStepperTot(dim,bound,targetSum);
		//System.out.println("step " + dim + " " + bound + " " + targetSum);
		final int[] x = stepper.first();
		if(null==x) {
			if(!checkSet.isEmpty()) {
				return false;
			}
		} else {
			do {
				int sum = 0;
				int lastXi = 0;
				for(final int xi: x) {
					if((xi<0)||(xi>bound)||(xi<lastXi)) {
						return false;
					}
					sum += xi;
					lastXi = xi;
				}
				if(targetSum!=sum) {
					return false;
				}
				final IntVec xv = new IntVec(x);
				//System.out.println("\t" + xv);
				if(!checkSet.contains(xv)) {
					return false;
				}
				checkSet.remove(xv);
			} while(stepper.advance(x));
			if(!checkSet.isEmpty()) {
				return false;
			}
		}
		return true;
	}
}
