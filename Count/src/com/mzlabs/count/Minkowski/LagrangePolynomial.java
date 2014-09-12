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

	private LagrangePolynomial() {
	}
	
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
	public static final BigRat eval(int[] b, final int[] z, int s, final int[] x) {
		final int n = z.length;
		b = Arrays.copyOf(b,n);
		BigRat prod = BigRat.ONE;
		int nePos = 0;
		while(s>0) {
			// find first coordinate of z to exceed b
			while((nePos<n)&&(z[nePos]<=b[nePos])) {
				++nePos;
			}
			if(nePos>=n) {
				// z==b, so zap out rest of wedge by grade level
				int sumDiff = 0;
				for(int i=0;i<n;++i) {
					sumDiff += x[i]-b[i];
				}
				// map sumDiffs of 1...n to zero and sumDiff of 0 to 1
				for(int i=0;i<s;++i) {
					final BigRat term = BigRat.ONE.subtract(BigRat.valueOf(sumDiff,i+1));
					prod = prod.multiply(term);
				}
				s = 0;
			} else {
				// have a difference in coordinate, shift up until we reach it
				while(b[nePos]<z[nePos]) {
					final BigRat c = BigRat.valueOf(x[nePos]-b[nePos],z[nePos]-b[nePos]);
					prod = prod.multiply(c);
					b[nePos] += 1;
					s -= 1;
				}
			}
		}
		return prod;
	}
}
