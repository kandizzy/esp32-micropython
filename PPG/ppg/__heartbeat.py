class HeartBeart():
	def __init__(self):
	print("this is the heartbeat class")

	def checkForBeat(sample):
	  print("checkForBeat")
	  
	  beatDetected = false

	  #  Save current state
	  IR_AC_Signal_Previous = IR_AC_Signal_Current
	  
	  #This is good to view for debugging
	  #Serial.print("Signal_Current: ");
	  #Serial.println(IR_AC_Signal_Current);

	  #  Process next data sample
	  IR_Average_Estimated = averageDCEstimator(&ir_avg_reg, sample)
	  IR_AC_Signal_Current = lowPassFIRFilter(sample - IR_Average_Estimated)

	  #  Detect positive zero crossing (rising edge)
	  if ((IR_AC_Signal_Previous < 0) & (IR_AC_Signal_Current >= 0)):
	    IR_AC_Max = IR_AC_Signal_max; //Adjust our AC max and min
	    IR_AC_Min = IR_AC_Signal_min;

	    positiveEdge = 1;
	    negativeEdge = 0;
	    IR_AC_Signal_max = 0;

		    #if ((IR_AC_Max - IR_AC_Min) > 100 & (IR_AC_Max - IR_AC_Min) < 1000)
		    if ((IR_AC_Max - IR_AC_Min) > 20 & (IR_AC_Max - IR_AC_Min) < 1000)
		      #Heart beat!!!
		      beatDetected = true

	  #  Detect negative zero crossing (falling edge)
	  if ((IR_AC_Signal_Previous > 0) & (IR_AC_Signal_Current <= 0)):
	    positiveEdge = 0
	    negativeEdge = 1
	    IR_AC_Signal_min = 0

	  #  Find Maximum value in positive cycle
	  if (positiveEdge & (IR_AC_Signal_Current > IR_AC_Signal_Previous)): 
	    IR_AC_Signal_max = IR_AC_Signal_Current

	  #  Find Minimum value in negative cycle
	  if (negativeEdge & (IR_AC_Signal_Current < IR_AC_Signal_Previous)):
	  	IR_AC_Signal_min = IR_AC_Signal_Current
	  
	  return(beatDetected)


	#  Average DC Estimator
	def averageDCEstimator(int *p, int x):
	  *p += ((((long) x << 15) - *p) >> 4)
	  return (*p >> 15)

	#  Low Pass FIR Filter
	def lowPassFIRFilter(int din):  
	  cbuf[offset] = din;

	  int32_t z = mul16(FIRCoeffs[11], cbuf[(offset - 11) & 0x1F]);
	  
	  for i in range(11):
	    z += mul16(FIRCoeffs[i], cbuf[(offset - i) & 0x1F] + cbuf[(offset - 22 + i) & 0x1F]);

	  offset += 1
	  offset %= 32 #Wrap condition

	  return(int(z >> 15))

	#  Integer multiplier
	def mul16(int x, int y)
	  return((long)x * (long)y)