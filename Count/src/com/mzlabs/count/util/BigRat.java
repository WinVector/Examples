package com.mzlabs.count.util;

import java.math.BigInteger;

public final class BigRat implements Comparable<BigRat> {
	public final BigInteger num;
	public final BigInteger den;
		
	public static final BigRat ZERO = new BigRat(BigInteger.ZERO,BigInteger.ONE);
	public static final BigRat ONE = new BigRat(BigInteger.ONE,BigInteger.ONE);
	
	private BigRat(final BigInteger num, final BigInteger den) {
		this.num = num;
		this.den = den;
	}
	
	public static BigRat valueOf(final BigInteger x) {
		return new BigRat(x,BigInteger.ONE);
	}

	public static BigRat valueOf(final BigInteger num, final BigInteger den) {
		final int cmpDen = BigInteger.ZERO.compareTo(den);
		if(cmpDen==0) {
			throw new IllegalArgumentException("zero denominator");
		}
		final int cmpNum = BigInteger.ZERO.compareTo(num);
		if(cmpNum==0) {
			return ZERO;
		}
		final BigInteger numAbs = num.abs();
		final BigInteger denAbs = den.abs();
		final boolean negative = cmpDen*cmpNum<0;
		if(BigInteger.ONE.compareTo(denAbs)==0) {
			return new BigRat(negative?numAbs.negate():numAbs,denAbs);
		} else {
			final BigInteger gcd = numAbs.gcd(denAbs);
			final BigInteger numLCM = numAbs.divide(gcd);
			return new BigRat(negative?numLCM.negate():numLCM,denAbs.divide(gcd));
		}
	}
	
	public static BigRat valueOf(final int num, final int den) {
		return valueOf(BigInteger.valueOf(num),BigInteger.valueOf(den));
	}
	
	public BigRat add(final BigRat o) {
		return valueOf(num.multiply(o.den).add(o.num.multiply(den)),den.multiply(o.den));
	}
	
	public BigRat subtract(final BigRat o) {
		return valueOf(num.multiply(o.den).subtract(o.num.multiply(den)),den.multiply(o.den));
	}
	
	public BigRat multiply(final BigRat o) {
		return valueOf(num.multiply(o.num),den.multiply(o.den));
	}
	
	@Override
	public String toString() {
		if(BigInteger.ONE.compareTo(den)==0) {
			return num.toString();
		} else {
			return num.toString() + "/" + den.toString();
		}
	}

	@Override
	public int compareTo(final BigRat o) {
		// dens are positive, so multiply through by them doesn't change order relns
		return num.multiply(o.den).compareTo(o.num.multiply(den));
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((BigRat)o)==0;
	}
	
	@Override
	public int hashCode() {
		return num.hashCode() + 5*den.hashCode();
	}
}
