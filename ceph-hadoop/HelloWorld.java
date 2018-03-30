import org.apache.hadoop.fs.ceph.CephFileSystem;
import org.apache.hadoop.fs.Path;
import java.net.URI;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
//import org.apache.hadoop.fs.ceph.CephFs;
public class HelloWorld {
  public static void main(String[]agrs)
    {
        try {
            Configuration conf = new Configuration();
            conf.set("ceph.auth.id", "admin");
            conf.set("ceph.conf.file", "/etc/ceph/ceph.conf");
            conf.set("ceph.data.pools", "hadoop1");
            conf.set("ceph.mon.address", "192.168.10.61:6789");
            conf.set("ceph.auth.keyfile", "/etc/ceph/admin.secret");
            
            URI uri = new URI("ceph://192.168.10.61:6789/");
            CephFileSystem fs = new CephFileSystem();
            fs.initialize(uri, conf);
            FileStatus[] st = fs.listStatus(new Path("/tmp/hive/hdfs/_tez_session_dir/437198fa-4282-470c-a994-1202bf427a8f/hive-hcatalog-core.jar"));
            System.out.println(st[0]);
        } 
        catch (Exception  e) {
            System.out.println(e);
            e.printStackTrace();
        }
    }
}
