package edu.mit.ll.catan_service;

import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.SimpleAdapter;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

import edu.mit.ll.catan_service.sda.apache.HttpClientSDA;


public class configActivity extends Activity {

    //List of users pulled from CATAN server
    JSONArray users = null;

    // Hashmap for ListView
    ArrayList<HashMap<String, String>> userList;


    /**
     * Called when the activity is first created.
     */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        userList = new ArrayList<HashMap<String, String>>();

        //Launch async process to fetch all users
        new GetUsers().execute();

        setContentView(R.layout.activity_config);


        //Get selection from listview and launch polling service
        ListView lv = (ListView) findViewById(R.id.list);
        lv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position,
                                    long id) {

                //Get Selection
                HashMap<String, String> contact = (HashMap<String, String>) parent.getItemAtPosition(position);
                Log.d(config.TAG, "Selected user id: " + contact.get("person_id"));

                //Launch the polling service (Catan pull daemon)
                Intent intent = new Intent(configActivity.this, CatanPullDaemon.class);
                intent.putExtra("person_id", contact.get("person_id"));
                startService(intent);
                finish();
            }
        });

    }


    private class GetUsers extends AsyncTask<Void, Void, Void> {
        String contents = null;

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Showing progress dialog
        }

        @Override
        protected Void doInBackground(Void... arg0) {
            String content = null;

            try {
                //Make request to server for all users and uuid on create
                String requestUrl = config.URL + "/all_users";
                Log.d(config.TAG, requestUrl);

                HttpClientSDA httpClient = new HttpClientSDA();
                HttpGet request = new HttpGet(requestUrl);

                try {
                    HttpResponse response;
                    response = httpClient.execute_sda(request);
                    HttpEntity entity = response.getEntity();

                    // Read the contents of an entity and return it as a String.
                    content = EntityUtils.toString(entity);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } catch (Exception ex) {
                ex.printStackTrace();
            }

            //Parse JSON response for user list
            if (content != null) {
                try {
                    JSONArray users = new JSONArray(content);

                    Log.d(config.TAG, "Number of users in db: " + String.valueOf(users.length()));

                    // looping through All Contacts
                    for (int i = 0; i < users.length(); i++) {
                        JSONObject c = users.getJSONObject(i);

                        String id = c.getString("person_id");
                        String name_given = c.getString("name_given");
                        String name_family = c.getString("name_family");
                        String age = c.getString("age");
                        String sex = c.getString("sex");

                        Log.d("CATAN", id + " " + name_given + " " + name_family + " " + sex + " " + age);

                        // tmp hashmap for single contact
                        HashMap<String, String> contact = new HashMap<String, String>();

                        // adding each child node to HashMap key => value
                        contact.put("person_id", id);
                        contact.put("name", name_given + " " + name_family);
                        contact.put("sex", sex);
                        contact.put("age", age);

                        // adding contact to contact list
                        userList.add(contact);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            } else {
                Log.e(config.TAG, "Couldn't get any data from the url");
            }

            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            /**
             * Updating parsed JSON data into ListView
             * */
            ListView list = (ListView) findViewById(R.id.list);
            ListAdapter adapter = new SimpleAdapter(
                    configActivity.this, userList,
                    R.layout.list_item, new String[]{"name", "sex", "age",
                    "person_id"}, new int[]{R.id.name, R.id.sex,
                    R.id.age});
            list.setAdapter(adapter);
        }

    }
}