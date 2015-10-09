package edu.mit.ll.catan_service.sda.apache;

import android.net.LocalSocket;
import android.net.LocalSocketAddress;
import android.util.Log;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;


/**
 * Created by rhousley on 7/23/15.
 */
public class socketSDA {
    private LocalSocket unixSocket;
    private OutputStream os;
    private InputStream is;

    socketSDA() throws IOException {
        // Establish unix socket to connect SDA Server
        unixSocket = new LocalSocket(LocalSocket.SOCKET_STREAM);
        LocalSocketAddress SDA_ServerAddress = new LocalSocketAddress(
                "/tmp/".concat("SDA"));
//        Log.d("SDA", SDA_ServerAddress.getName());
        unixSocket.connect(SDA_ServerAddress);
    }

    public boolean isConnected() {
        return unixSocket.isConnected();
    }

    public byte[] recv() throws IOException {
        if (isConnected()) {
            byte[] baLength = new byte[4];
            is = unixSocket.getInputStream();

            //@Todo: make sure 4 byte return occurs
            is.read(baLength, 0, 4);
            int pktLength = ByteBuffer.wrap(baLength).order(ByteOrder.LITTLE_ENDIAN).getInt();

            //@Todo: make sure pktLength pkt is returned, and add timeout
            byte[] received = new byte[pktLength];
            is.read(received, 0, pktLength);
            return received;
        } else {
            throw new IOException();
        }
    }

    public void send(byte[] headerData) throws IOException {
        if (isConnected()) {
            byte length_ba[] = new byte[4];
            length_ba = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(headerData.length).array(); //intToByteArray(headerData.length);

           // Write out
            os = unixSocket.getOutputStream();
            os.write(length_ba);
            os.flush();
            os.write(headerData);
            os.flush();
        }
    }
}
