
import java.sql.*;

public class SampleVulnerable {
    // Hardcoded Secret
    private static final String DB_PASSWORD = "SuperSecretPassword123!";

    public void getUser(String userId) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/db", "root", DB_PASSWORD);
            Statement stmt = conn.createStatement();
            // SQL Injection Vulnerability
            String query = "SELECT * FROM users WHERE id = '" + userId + "'";
            ResultSet rs = stmt.executeQuery(query);
        } catch (Exception e) {
            // Code Smell: Empty catch block
        }
    }
}
