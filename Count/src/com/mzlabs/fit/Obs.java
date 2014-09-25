package com.mzlabs.fit;

import java.util.Arrays;

public final class Obs {
	public final double[] x;
	public final double y;
	public final double wt;
	
	public Obs(final double[] x, final double y, final double wt) {
		this.x = Arrays.copyOf(x,x.length);
		this.y = y;
		this.wt = wt;
	}
	
	/**
	 * 
	 * @param soln soln.length==x.length+1
	 * @param x
	 * @return
	 */
	public static double dot(final double soln[], final double[] x) {
		final int n = x.length;
		if(soln.length!=n+1) {
			throw new IllegalArgumentException();
		}
		double sum = 0.0;
		for(int i=0;i<=n;++i) {
			final double xi = i<n?x[i]:1.0;
			sum += xi*soln[i];
		}
		return sum;		
	}
	
	/**
	 * 
	 * @param soln.length==x.length+1
	 * @return
	 */
	public double dot(final double[] soln) {
		return dot(soln,x);
	}
	
	@Override
	public String toString() {
		final StringBuilder b = new StringBuilder();
		b.append("" + wt + ":[");
		for(final double xi:x) {
			b.append(" " + xi);
		}
		b.append(" ]-> " + y);
		return b.toString();
	}
}