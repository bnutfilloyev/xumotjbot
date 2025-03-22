# XumotjBot

<div align="center">
  <img src="https://via.placeholder.com/200x200/3F51B5/FFFFFF?text=XumotjBot" alt="XumotjBot Logo" width="200" height="200">
  <h3>A powerful Telegram bot for managing voting contests and nominations</h3>
  <p>
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#api-documentation">API Documentation</a> •
    <a href="#deployment">Deployment</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
</div>

## Features

XumotjBot is a comprehensive solution for managing voting contests on Telegram. It enables users to:

- **Browse Nominations** - View available contest categories and nominations
- **Vote for Participants** - Cast votes for favorite participants in each nomination
- **Track Vote Counts** - See real-time vote tallies for all participants
- **Change Votes** - Modify votes within the same nomination
- **User Authentication** - Secure user verification via contact sharing
- **Administrative Dashboard** - Manage nominations, participants, and view analytics

### Key Technical Capabilities

- ✅ **MongoDB Integration** - Efficient NoSQL storage for all contest data
- ✅ **Aiogram 3.x Support** - Built on the latest version of the Aiogram framework
- ✅ **Admin Panel** - Web interface for managing all aspects of the contest
- ✅ **Docker Support** - Easy deployment with Docker and Docker Compose
- ✅ **Asynchronous Architecture** - High performance with async/await patterns
- ✅ **Configurable Voting Rules** - Customize voting limitations and behavior

## Architecture

XumotjBot follows a modular architecture pattern, separating concerns into distinct components:

```
xumotjbot/
├── bot/                     # Telegram bot application
│   ├── filters/             # Custom Aiogram filters
│   ├── handlers/            # Command and callback handlers
│   ├── keyboards/           # Inline keyboard builders
│   ├── middlewares/         # Request middlewares
│   ├── structures/          # Data models and database access
│   └── utils/               # Helper functions
├── admin/                   # Admin panel application
│   ├── api/                 # REST API endpoints
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   └── views/               # Admin interface views
├── scripts/                 # Utility scripts for maintenance
├── tests/                   # Automated tests
└── docker/                  # Docker configuration files
```

### Data Flow

![Architecture Diagram](https://via.placeholder.com/800x400/EFEFEF/333333?text=XumotjBot+Architecture+Diagram)

1. User interacts with the bot via Telegram
2. Bot processes commands and callbacks through handlers
3. Database operations are executed through the structures layer
4. Admin panel provides a web interface to manage all data
5. MongoDB stores all persistent data (users, nominations, votes)

## Installation

### Prerequisites

- Python 3.9+
- MongoDB 4.4+
- Docker and Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/xumotjbot.git
cd xumotjbot
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration values
```

5. **Run the bot**

```bash
cd bot
python main.py
```

6. **Run the admin panel (separate terminal)**

```bash
cd admin
python app.py
```

### Docker Setup

1. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

This will start:
- The Telegram bot
- MongoDB database
- Admin panel
- Mongo Express (optional web interface for MongoDB)

## Usage

### Bot Commands

- `/start` - Start the bot and get introduction
- `/help` - Display available commands and instructions
- `/nominations` - View all active nominations
- `/vote` - Start the voting process
- `/results` - View current vote tallies
- `/profile` - View your voting status

### Admin Panel

The admin panel is accessible at `http://your-server:8000/admin` with the credentials configured in your `.env` file.

Key features include:

- **Dashboard** - Overview of system statistics
- **Nominations** - Create, edit and manage nominations
- **Participants** - Add and remove participants for each nomination
- **Users** - View registered bot users
- **Votes** - Monitor and manage user votes
- **Settings** - Configure general bot settings

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Telegram Bot API token | Required |
| `ADMIN_IDS` | Comma-separated list of admin Telegram IDs | Required |
| `DEBUG` | Enable debug mode | `False` |
| `CHANNEL_ID` | Telegram channel ID for announcements | Required |
| `MONGODB_HOST` | MongoDB host | `localhost` |
| `MONGODB_PORT` | MongoDB port | `27017` |
| `MONGODB_USERNAME` | MongoDB username | ` ` |
| `MONGODB_PASSWORD` | MongoDB password | ` ` |
| `MONGODB_DATABASE` | MongoDB database name | `xumotjbot` |
| `MONGO_URI` | Full MongoDB connection URI (overrides other DB settings) | ` ` |
| `ADMIN_USERNAME` | Admin panel username | `admin` |
| `ADMIN_PASSWORD` | Admin panel password | `admin` |
| `SECRET_KEY` | Secret key for admin panel sessions | Random |
| `HOST` | Admin panel host | `127.0.0.1` |
| `PORT` | Admin panel port | `8000` |
| `ADMIN_BASE_URL` | Admin panel base URL path | `/admin` |

## API Documentation

### Bot Structure

The bot uses the Aiogram 3.x callback query system. Key components:

#### Callback Data Classes

```python
class NominationCallback(CallbackData, prefix="nomination"):
    id: str
    name: str

class ParticipantCallback(CallbackData, prefix="participant"):
    nomination_id: str
    name: str
```

#### Database Methods

| Method | Description |
|--------|-------------|
| `get_user(user_id)` | Retrieves user by Telegram ID |
| `user_update(user_id, data)` | Updates user data |
| `get_nominations()` | Gets all active nominations |
| `get_nomination(nomination_id)` | Gets a specific nomination |
| `get_participants(nomination_id)` | Gets participants for a nomination |
| `add_vote(nomination_id, participant_name, user_id)` | Records a vote |

### Admin API Endpoints

The admin panel provides a REST API for programmatic access:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/nominations` | GET | Retrieve all nominations |
| `/api/nominations/{id}` | GET | Get nomination details |
| `/api/nominations` | POST | Create a new nomination |
| `/api/nominations/{id}` | PUT | Update a nomination |
| `/api/votes/stats` | GET | Get voting statistics |
| `/api/export/results` | GET | Export results in CSV format |

## Deployment

### Production Deployment Recommendations

1. **Use Docker Compose in Production**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **Set up Nginx as a reverse proxy**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Enable SSL with Let's Encrypt**

```bash
certbot --nginx -d your-domain.com
```

4. **Set up regular MongoDB backups**

```bash
# Add to crontab
0 3 * * * /path/to/xumotjbot/scripts/backup.sh
```

### Scaling Considerations

- For high-load scenarios, consider:
  - Implementing Redis caching
  - Setting up MongoDB replication
  - Using multiple bot instances behind a load balancer

## Maintenance

### Database Backups

Run the backup script periodically:

```bash
./scripts/backup.sh
```

### Updating the Bot

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**
   - Check if the bot is running (`docker-compose ps`)
   - Verify the Telegram token in `.env`
   - Check the logs (`docker-compose logs bot`)

2. **Cannot connect to the admin panel**
   - Ensure the admin panel container is running
   - Check the firewall settings
   - Verify the admin credentials in `.env`

3. **Database connection errors**
   - Check MongoDB connection settings
   - Ensure MongoDB is running (`docker-compose logs mongodb`)
   - Verify network connectivity between containers

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code follows the existing style and passes all tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [Motor](https://github.com/mongodb/motor) - Async MongoDB driver
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [Python](https://www.python.org/) - Programming language

---

<div align="center">
  <p>Developed with ❤️ by <a href="https://github.com/yourusername">Your Name</a></p>
  <p>
    <a href="https://github.com/yourusername">GitHub</a> •
    <a href="https://t.me/yourusername">Telegram</a> •
    <a href="mailto:your.email@example.com">Email</a>
  </p>
</div>
