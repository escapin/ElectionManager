package de.uni.trier.infsec.utils;

import java.nio.charset.Charset;

public class Utilities {
	
	public static final String byteArrayToHexString(byte[] b) {
		final String hexChar = "0123456789ABCDEF";

		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < b.length; i++)
		{
			sb.append(hexChar.charAt((b[i] >> 4) & 0x0f));
			sb.append(hexChar.charAt(b[i] & 0x0f));
		}
		return sb.toString();
	}
	
	public static byte[] hexStringToByteArray(String s) {
	    int len = s.length();
	    byte[] data = new byte[len / 2];
	    for (int i = 0; i < len; i += 2) {
	        data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i+1), 16));
	    }
	    return data;
	}
	
	public static byte[] stringAsBytes(String str) {
		return str.getBytes(Charset.forName("UTF-8"));
	}
	
	public static String bytesAsString(byte[] bytes) {
		return new String(bytes, Charset.forName("UTF-8"));
	}
	
//	/**
//	 *	Helper to enlarge the Array which stores the credentials. Used to avoid usage of Lists 
//	 */
//	public static byte[][] enlargeArray(byte[][] theArray, int i) {
//		if (theArray.length > i) return theArray;
//		
//		byte[][] newArray = new byte[i+1][theArray[0].length];
//		for (int j = 0; j < theArray.length; j++) {
//			newArray[j] = theArray[j];
//		}
//		return newArray;
//	}
	
	/**
	 *	Checks two Arrays for equality 
	 */
	public static boolean arrayEqual(byte[] a1, byte[] a2) {
		if(a1==null && a2==null) return true;
		if(a1==null || a2==null) return false;
		if (a1.length != a2.length) return false;
		for (int i = 0; i < a1.length; i++) {
			if (a1[i] != a2[i]) return false;
		}
		return true;
	}
	
	public static boolean arrayEmpty(byte[] array) {
		for (int i = 0; i < array.length; i++) {
			if (array[i] != 0x00) return false;
		}
		return true;
	}

}
