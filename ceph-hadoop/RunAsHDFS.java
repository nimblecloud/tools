import java.security.PrivilegedExceptionAction;

import org.apache.hadoop.conf.*;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.ceph.CephFileSystem;
import java.net.URI;

public class RunAsHDFS {

    public static void main(String args[]) {

        try {
            UserGroupInformation ugi
                = UserGroupInformation.createRemoteUser("hbase");

            ugi.doAs(new PrivilegedExceptionAction<Void>() {

                public Void run() throws Exception {

                    Configuration conf = new Configuration();
                    conf.set("fs.defaultFS", "ceph://192.168.10.61:6789");
                    // conf.set("hadoop.job.ugi", "hbase");
                    conf.set("ceph.auth.id", "admin");
                    conf.set("ceph.conf.file", "/etc/ceph/ceph.conf");
                    conf.set("ceph.data.pools", "hadoop1");
                    conf.set("ceph.mon.address", "192.168.10.61:6789");
                    conf.set("ceph.auth.keyfile", "/etc/ceph/admin.secret");

                    conf.set("fs.ceph.impl", "org.apache.hadoop.fs.ceph.CephFileSystem");

                    FileSystem fs = FileSystem.get(conf);

                    FileStatus[] st = fs.listStatus(new Path("/tmp/hive/hdfs/_tez_session_dir/437198fa-4282-470c-a994-1202bf427a8f/hive-hcatalog-core.jar"));
                    System.out.println(st[0]);

                    return null;
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}