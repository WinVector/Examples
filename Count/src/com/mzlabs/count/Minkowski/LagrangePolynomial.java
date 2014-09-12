package com.mzlabs.count.Minkowski;

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
	public static final BigRat eval(final int[] b, final int[] z, final int s, final int[] x) {
		final int n = z.length;
		{ // confirm pre-conditions (helps localize any errors) 
			if(s<0) {
				throw new IllegalArgumentException("z<0");
			}
			int checkSum = 0;
			for(int i=0;i<n;++i) {
				if(z[i]<b[i]) {
					throw new IllegalArgumentException("b not <= z");
				}
				checkSum += z[i]-b[i];
			}
			if(checkSum>s) {
				throw new IllegalArgumentException("sum(z-b)>s");
			}
		}
		// evaluate polynomial (named by b,z,s) at x
		int degreeRemaining = s;
		BigRat prod = BigRat.ONE;
		int sumDiff = 0;
		for(int i=0;i<n;++i) {
			int bi = b[i];
			while(bi<z[i]) {
				final BigRat c = BigRat.valueOf(x[i]-bi,z[i]-bi);
				prod = prod.multiply(c);
				bi += 1;
				degreeRemaining -= 1;
			}
			sumDiff += x[i]-z[i];
		}
		while(degreeRemaining>0) { // z==b, so zap out rest of wedge by grade levels
			final BigRat term = BigRat.ONE.subtract(BigRat.valueOf(sumDiff,degreeRemaining));
			prod = prod.multiply(term);
			--degreeRemaining;
		}
		return prod;
	}
}
