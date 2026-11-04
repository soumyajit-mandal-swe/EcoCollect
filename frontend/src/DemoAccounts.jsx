
import { Users } from 'lucide-react';

const accounts = [
  {
    name: 'Soumyajit Mandal',
    email: 'soumyajit@example.com',
  },
  {
    name: 'Sourja Sinha',
    email: 'sourja@example.com',
  },
  {
    name: 'Harsh Kumar Jha',
    email: 'harsh@example.com',
  },
  {
    name: 'Sayandip Rout',
    email: 'sayandip@example.com',
  },
  {
    name: 'Aditya Chaubey',
    email: 'aditya@example.com',
  },
];

export default function DemoAccounts() {
  return (
    <section
      className="demo-accounts"
      aria-label="EcoCollect team"
    >
      <div className="demo-accounts-heading">
        <Users size={18} />
        <div>
          <h3>Meet the EcoCollect team</h3>
          <p>Our DBMS mini-project team.</p>
        </div>
      </div>

      <ul>
        {accounts.map((account) => (
          <li key={account.email}>
            <span>
              <strong>{account.name}</strong>
              <span className="demo-email">
                {account.email}
              </span>
            </span>
            <span className="demo-role">User</span>
          </li>
        ))}
      </ul>

      <div className="demo-passwords">
        <span>
          Admin email
          <code>admin@example.com</code>
        </span>
      </div>
    </section>
  );
}
