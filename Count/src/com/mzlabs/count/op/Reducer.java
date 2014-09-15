package com.mzlabs.count.op;

import java.math.BigInteger;

public interface Reducer {
	BigInteger reduce(IntFunc f, Sequencer s);
}
