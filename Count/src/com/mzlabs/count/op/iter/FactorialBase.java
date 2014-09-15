package com.mzlabs.count.op.iter;

import java.math.BigInteger;

public class FactorialBase {
	public final int dim;
	private final BigInteger[] factorial;
	
	FactorialBase(final int dim) {
		this.dim = dim;
		factorial = new BigInteger[Math.max(2,dim+1)];
		factorial[0] = BigInteger.ONE;
		factorial[1] = BigInteger.ONE;
		for(int i=2;i<factorial.length;++i) {
			factorial[i] = factorial[i-1].multiply(BigInteger.valueOf(i));
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
}
