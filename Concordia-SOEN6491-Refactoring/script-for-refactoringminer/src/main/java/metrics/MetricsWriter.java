package metrics;

import com.github.mauricioaniche.ck.CKNotifier;
public interface MetricsWriter extends CKNotifier{
    void finish();
}
