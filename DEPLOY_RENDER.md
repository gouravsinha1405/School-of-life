# Deploying to Render

This guide will help you deploy the Lebensschule meditation app to Render.

## Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. A [Groq API key](https://console.groq.com/) for the LLM service
3. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Push Your Code to Git

If you haven't already, initialize a git repository and push to GitHub/GitLab:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Deploy via Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Blueprint"**
3. Connect your Git repository
4. Render will automatically detect the `render.yaml` file
5. Click **"Apply"**

### 3. Configure Environment Variables

After deployment starts, you need to manually set the `GROQ_API_KEY`:

1. Go to your **lebensschule-backend** service in Render
2. Navigate to **Environment** tab
3. Find `GROQ_API_KEY` and add your actual API key
4. Click **"Save Changes"** (this will trigger a redeploy)

### 4. Wait for Deployment

Render will:
- Create a PostgreSQL database
- Build and deploy the backend (with automatic migrations)
- Build and deploy the frontend
- Link all services together

This typically takes 5-10 minutes.

### 5. Access Your Application

Once deployed, you'll get URLs like:
- Frontend: `https://lebensschule-frontend.onrender.com`
- Backend API: `https://lebensschule-backend.onrender.com`

## Important Notes

### Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Database limited to 1GB storage

### Security Recommendations

1. **Change JWT Secret**: The `JWT_SECRET` is auto-generated, but you can change it in the backend environment variables
2. **Update CORS**: The `CORS_ORIGINS` is automatically set to your frontend URL
3. **Database Backups**: Enable automatic backups in Render's database settings

### Monitoring

- Check logs: Go to each service → **Logs** tab
- Database metrics: Go to database → **Metrics** tab
- Health checks: Backend has a health check at `/`

## Troubleshooting

### Backend Won't Start
- Check that `GROQ_API_KEY` is set
- View logs for migration errors
- Ensure PostgreSQL database is running

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is deployed and running

### Database Connection Errors
- The DATABASE_URL is automatically configured
- Check database service is running
- Verify connection string format

## Scaling

To upgrade from free tier:
1. Go to each service
2. Click **"Settings"** → **"Instance Type"**
3. Choose a paid plan (starts at $7/month per service)

## Cost Estimate

- Free tier: $0 (with limitations)
- Starter tier: ~$21/month
  - Database: $7/month
  - Backend: $7/month
  - Frontend: $7/month

## Alternative: Manual Deployment

If you prefer manual setup over the blueprint:

1. Create PostgreSQL database first
2. Create Backend web service:
   - Type: Docker
   - Connect repository
   - Set Docker context to `./backend`
   - Add all environment variables manually
3. Create Frontend web service:
   - Type: Docker
   - Connect repository
   - Set Docker context to `./frontend`
   - Set `NEXT_PUBLIC_API_BASE_URL` to backend URL

## Next Steps

After deployment:
1. Test the application
2. Create your first user via the registration page
3. Set up custom domain (optional, requires paid plan)
4. Configure monitoring and alerts
5. Set up automated backups

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
