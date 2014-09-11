package com.mzlabs.count.Minkowski;

import java.util.Arrays;

import com.mzlabs.count.util.BigRat;

/**
 * The unique polynomial of degree |{x|0<=x<s, sum(x)<=s, x integral}|
 * in z.length variables that is non-zero at x=z and zero on the rest of x s.t. 0<=x sum(x)<=s
 * @author johnmount
 *
 */
public final class LagrangePolynomial {

	/**
	 * This function is a polynomial in b.length variables of degree s.
	 * 
	 * eval(b,z,s,x) = 1 if x==b and 0 for other points in the x>=b sum(x-b)<=s wedge
	 * @param b base to eval from
	 * @param z name of polynomial z.length==b.length , z[i]>=b[i] and sum(z[i]-b[i])<=s
	 * @param s degree of polynomial
	 * @param x where to evaluate polynomial
	 * @return f(x)
	 */
	public static final BigRat eval(final int[] b, final int[] z, final int s, final int[] x) {
		if(s<=0) {
			return BigRat.ONE;
		}
		final int n = z.length;
		// find first coordinate of z to exceed b
		int nePos = 0;
		while((nePos<n)&&(z[nePos]<=b[nePos])) {
			++nePos;
		}
		if(nePos>=n) {
			// z==b, so zap out rest of wedge by grade level
			BigRat prod = BigRat.ONE;
			int sumDiff = 0;
			for(int i=0;i<n;++i) {
				sumDiff += x[i]-b[i];
			}
			// map sumDiffs of 1...n to zero and sumDiff of 0 to 1
			for(int i=0;i<s;++i) {
				final BigRat term = BigRat.ONE.subtract(BigRat.valueOf(sumDiff,i+1));
				prod = prod.multiply(term);
			}
			return prod;
		} else {
			// have a difference in coordinate, recurse
			final BigRat c = BigRat.valueOf(x[nePos]-b[nePos],z[nePos]-b[nePos]);
			final int[] subB = Arrays.copyOf(b,n);
			subB[nePos] += 1;
			final BigRat sub = eval(subB,z,s-1,x);
			return c.multiply(sub);
		}
	}
	
	
	public static void main(final String[] args) {
		// TODO: move to test
		final int[] base = { 20, 20, 8, 12, 12 };
		final int dim = base.length;
		final int degree = 4;
		final int[] b2 = new int[dim];
		Arrays.fill(b2,100);
		final SumStepper stepper = new SumStepper(degree);
		final int[] d = stepper.first(base.length);
		final int[] z = new int[base.length];
		do {
			for(int i=0;i<z.length;++i) {
				z[i] = base[i] + d[i];
			}
			final BigRat confirmOne = LagrangePolynomial.eval(base,z,degree,z);
			if(BigRat.ONE.compareTo(confirmOne)!=0) {
				throw new IllegalStateException("didn't evalute to 1 at correct point");
			}
			final int[] d2 = stepper.first(base.length);
			final int[] z2 = stepper.first(base.length);
			do {
				boolean equalsz = true;
				for(int i=0;i<z2.length;++i) {
					z2[i] = base[i] + d2[i];
					if(z2[i]!=z[i]) {
						equalsz = false;
					}
				}
				if(!equalsz) {
					final BigRat confirmZero = LagrangePolynomial.eval(base,z,degree,z2);
					if(BigRat.ZERO.compareTo(confirmZero)!=0) {
						throw new IllegalStateException("didn't evalute to 0 at correct point");
					}
				}
			} while(stepper.next(d2));
		} while(stepper.next(d));
	}
}
