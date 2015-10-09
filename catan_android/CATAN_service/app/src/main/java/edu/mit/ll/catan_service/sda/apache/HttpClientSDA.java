package edu.mit.ll.catan_service.sda.apache;

import android.util.Base64;
import android.util.Log;

import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;

import java.io.IOException;
import java.util.Arrays;

/**
 * Created by rhousley on 7/22/15.
 */

public class HttpClientSDA extends DefaultHttpClient {

    private int logLevel = Log.DEBUG;
    private int queryMax = 1000; // Prevents query explosion

    public void setLogLevel(int level) throws IOException {
        if ((level >= Log.VERBOSE) && (level <= Log.ASSERT)) {
            logLevel = level;
        }
        else {
            // If an inappropriate level is given, throw an error
            throw new IOException();
        }
    }

    public int getLogLevel() {
        return logLevel;
    }

    public void setQueryMax(int max) throws IOException {
        if (max > 0) {
            queryMax = max;
        }
        else
            throw new IOException();

    }

    public int getQueryMax() {
        return queryMax;
    }

    private Header getSDAHeader(HttpResponse response){
        Header[] headers = response.getAllHeaders();
        boolean foundFlag = false;

        if (logLevel <= Log.DEBUG){
            try {
                Log.d("SDA", "Header Length: " + headers.length + "     Headers contents" +
                        response.getEntity().getContent().toString());
                Log.d("SDA", "Headers:");
            } catch (IOException e) {
                Log.d("SDA", "Unable to fetch headers' contents");
            }
        }

        for (Header h: headers) {
            if (logLevel >= Log.DEBUG)
                Log.d("SDA", "|      Name: " + h.getName() + " Value: " + h.getValue());

            if (h.getName().equalsIgnoreCase("SDA"))
                return h;
        }
        return null;
    }

    /**
     * Sends a decoded SDA header over an SDA socket to a listening SDA server
     * @param sdaHeader
     * @return Base64 Encoded header from SDA local server
     * @throws IOException
     */
    private String getHeaderFromTEE(Header sdaHeader) throws IOException {
        String hData = sdaHeader.getValue();

        // Header arrives Base64 Encoded, decode it
        byte[] decodedHeader = Base64.decode(hData, Base64.DEFAULT);


        if (logLevel >= Log.DEBUG) {
            Log.d("SDA", "Incoming Header (in): " + Arrays.toString(decodedHeader));
        }

        // Make IPC call to SDA server with header data
        socketSDA s = new socketSDA(); // Will throw ioexception if server isnt listening
        s.send(decodedHeader);

        // Get returned data @TODO: make sure it returns something
        byte[] outHeader = s.recv();

        if (logLevel >= Log.DEBUG) {
            Log.d("SDA", "Outgoing Header: " + Arrays.toString(outHeader));
        }

        return Base64.encodeToString(outHeader, Base64.NO_WRAP);
    }


//    public HttpResponse execute_sda(HttpHost host, HttpRequest request, HttpContext context) throws IOException, ClientProtocolException {
//        HttpResponse response;
//        int queryCount = 0;
//
//        // Check if unauthorized response
//        while ((response = execute(host, request, context))
//                .getStatusLine().getStatusCode()  == HttpStatus.SC_UNAUTHORIZED) {
//
//            if (queryCount >= queryMax) {
//                throw new RuntimeException("Query limit exceeded");
//            }
//
//            Header sdaHeader;
//            if ((sdaHeader = getSDAHeader(response)) == null)
//                break; // Non-SDA message that returned an unauthorized response
//            else {
//                String ipcReturnedHeader = getHeaderFromTEE(sdaHeader);
//
//                // Append the new header to the new request
//                request.addHeader("SDA", ipcReturnedHeader);
//            }
//            queryCount++;
//        }
//        return response;
//    }
//
//    public HttpResponse execute_sda(HttpHost host, HttpRequest request) throws IOException, ClientProtocolException {
//        HttpResponse response;
//        int queryCount = 0;
//
//        // Check if unauthorized response
//        while ((response = execute(host, request))
//                .getStatusLine().getStatusCode()  == HttpStatus.SC_UNAUTHORIZED) {
//
//            if (queryCount >= queryMax) {
//                throw new RuntimeException("Query limit exceeded");
//            }
//
//            Header sdaHeader;
//            if ((sdaHeader = getSDAHeader(response)) == null)
//                break; // Non-SDA message that returned an unauthorized response
//            else {
//                String ipcReturnedHeader = getHeaderFromTEE(sdaHeader);
//
//                // Append the new header to the new request
//                request.addHeader("SDA", ipcReturnedHeader);
//            }
//            queryCount++;
//        }
//        return response;
//    }
//
//    public HttpResponse execute_sda(HttpUriRequest uri, HttpContext context) throws IOException, ClientProtocolException {
//        HttpResponse response;
//        int queryCount = 0;
//
//        // Check if unauthorized response
//        while ((response = execute(uri, context))
//                .getStatusLine().getStatusCode()  == HttpStatus.SC_UNAUTHORIZED) {
//
//            if (queryCount >= queryMax) {
//                throw new RuntimeException("Query limit exceeded");
//            }
//
//            Header sdaHeader;
//            if ((sdaHeader = getSDAHeader(response)) == null)
//                break; // Non-SDA message that returned an unauthorized response
//            else {
//                String ipcReturnedHeader = getHeaderFromTEE(sdaHeader);
//
//                // Append the new header to the new request
//                uri.addHeader("SDA", ipcReturnedHeader);
//            }
//            queryCount++;
//        }
//        return response;
//    }

    public HttpResponse execute_sda(HttpUriRequest uri) throws IOException {
        HttpResponse response;
        int queryCount = 0;

        // Check if unauthorized response
        while ((response = execute(uri))
                .getStatusLine().getStatusCode()  == HttpStatus.SC_UNAUTHORIZED) {

            if (queryCount >= queryMax)
                throw new RuntimeException("Query limit exceeded");

            if (logLevel >= Log.DEBUG)
                Log.d("SDA", "Status: " + response.getStatusLine().toString());

            Header sdaHeader;
            if ((sdaHeader = getSDAHeader(response)) == null)
                break; // Non-SDA message, return response
            else
                uri.addHeader("SDA", getHeaderFromTEE(sdaHeader));

            queryCount++;
        }
        return response;
    }



}
