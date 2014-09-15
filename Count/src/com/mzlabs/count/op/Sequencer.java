package com.mzlabs.count.op;

public interface Sequencer {
	/** 
	 * 
	 * @return first vector in sequence, null if there are none
	 */
	int[] first();
	
	/**
	 * 
	 * @param x current date (x.length = first().length)
	 * @return alter x to next state and return true if x is valid (false means sequencing is over)
	 */
	boolean advance(int[] x);
}
