package edu.mit.ll.catan_service;

import android.app.IntentService;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

/**
 * Created by rhousley on 8/25/15.
 */
import android.app.Service;
import android.content.Intent;
import android.net.Uri;
import android.os.IBinder;
import android.util.Log;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import edu.mit.ll.catan_service.sda.apache.HttpClientSDA;

public class CatanPullDaemon extends IntentService{

    String id = null;
    String globalstamp="0";
    int notifyCount=0;
    boolean isFirst = true;
    
    // Must create a default constructor
    public CatanPullDaemon() {
        // Used to name the worker thread, important only for debugging.
        super("catan-service");
    }

    @Override
    public void onCreate() {
        super.onCreate(); // if you override onCreate(), make sure to call super().
        // If a Context object is needed, call getApplicationContext() here.
    }

    @Override
    protected void onHandleIntent(Intent intent) {

        id = intent.getStringExtra("person_id");
        Log.d(config.TAG, "In daemon. Person id is "+ id);

        //Setup a timer to check server for announcements
        Timer myTimer = new Timer();
        checkForNewTimerTask task = new checkForNewTimerTask();
        myTimer.scheduleAtFixedRate(task, 0, config.requestPeriod);
    }

    /* Timer class for repeatedly querying catan server */
    private class checkForNewTimerTask extends TimerTask {
        @Override
        public void run() {
            String content = null;

            // Create Presence Request URL
            String requestUrl = config.URL + "/messages/?pid=" + id + "&ts=" + globalstamp;
            Log.d("CATAN", requestUrl);

            HttpClientSDA httpClient = new HttpClientSDA();

            // Disable redirects as they are enabled by default
            //  (old SDA server redirected for sessions)
            HttpParams params = new BasicHttpParams();
            params.setParameter("http.protocol.handle-redirects", false);
            httpClient.setParams(params);

            HttpGet request = new HttpGet(requestUrl);
            try {
                // If the redirect is a redirect, follow it
                //      (not necessary for servers that don't redirect)
                HttpResponse response;
                while ((response = httpClient.execute_sda(request)).getStatusLine().getStatusCode() == HttpStatus.SC_MOVED_TEMPORARILY) {
                    requestUrl = response.getHeaders("Location")[0].getValue();
                    request = new HttpGet(requestUrl);
                }

                switch (response.getStatusLine().getStatusCode()) {
                    case (HttpStatus.SC_OK):
                        Log.d(config.TAG, "Authenticated and able to connect to server");
                        HttpEntity entity = response.getEntity();

                        // Read the contents of an entity and return it as a String.
                        content = EntityUtils.toString(entity);
                        break;

                    case (HttpStatus.SC_FORBIDDEN):
                        Log.d(config.TAG, "You're authenticated, but you do not have access to this page");
                        break;

                    default:
                        Log.d(config.TAG, "You are not Authenticated");
                }
                Log.d("CATAN", "Status: " + response.getStatusLine().toString());

            } catch (IOException e) {
            }

            if (content != null) {
                Log.d(config.TAG, content);
                if (!isFirst) {
                    try {

                        JSONObject c = new JSONObject(content);
                        globalstamp = c.getString("timestamp");

                        String personal_messages = c.getString("personal");
                        JSONArray personal = new JSONArray(personal_messages);
                        Log.d(config.TAG, "personal length " + personal.length());
                        for (int i = 0; i < personal.length(); i++) {
                            JSONObject personal_mes = personal.getJSONObject(i);
                            String title = personal_mes.getString("status");
                            String content_text = personal_mes.getString("person_message");
                            String text_stamp = personal_mes.getString("timestamp_text");

                            Log.d(config.TAG, "Title: " + title + " Content: " + content_text);
                            notifyMessage(title, content_text);

                        }

                        String global_messages = c.getString("global");
                        JSONArray global = new JSONArray(global_messages);
                        for (int i = 0; i < global.length(); i++) {
                            JSONObject personal_mes = personal.getJSONObject(i);
                            String title = personal_mes.getString("title");
                            String content_text = personal_mes.getString("content");
                            String submitter = personal_mes.getString("submitter_name");
                            String submitter_org = personal_mes.getString("submitter_organization");

                            Log.d(config.TAG, "Global Title: " + title + " Content: " + content_text);
                            notifyMessage(title, content_text + "\n" + submitter + ", " + submitter_org);

                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                } else {
                    // Burn the first message set so not overnotified
                    JSONObject c = null;
                    try {
                        c = new JSONObject(content);
                        globalstamp = String.valueOf(c.getInt("timestamp"));
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    isFirst = false;
                }
            }
        }
    }

    public void notifyMessage(String title, String text){
        //        String contentText = "CATAN announcement";
        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        Notification notification = new Notification(R.drawable.ic_launcher,
                "New CATAN Notification", System.currentTimeMillis());
        Intent newintent = new Intent(Intent.ACTION_VIEW,
                Uri.parse(config.URL + "/announcements"));
        notification.setLatestEventInfo(this, title, text,
                PendingIntent.getActivity(this, 1, newintent, 0));

        manager.notify(notifyCount, notification);
        notifyCount++;
    }


}