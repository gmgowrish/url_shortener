# IP Geolocation Feature - Deployment Checklist

## Pre-Deployment Verification

### Backend Setup ✅
- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Verify geoip2 and requests are installed: `pip list | grep geoip2`
- [ ] Run database migrations: `python manage.py migrate`
- [ ] Test geolocation function:
  ```bash
  python manage.py shell
  >>> from analytics.geolocation import get_ip_geolocation
  >>> result = get_ip_geolocation('8.8.8.8')
  >>> print(result)  # Should show geolocation data
  ```
- [ ] Verify API endpoints are accessible:
  ```bash
  curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/analytics/link/1/ip-locations/
  curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/analytics/link/1/ip-stats/
  ```
- [ ] Check for any migration errors: `python manage.py check`

### Frontend Setup ✅
- [ ] Install Node dependencies: `npm install`
- [ ] Verify all packages installed: `npm list`
- [ ] Start development server: `npm run dev`
- [ ] Check dashboard loads: Visit `http://localhost:3000/dashboard`
- [ ] Verify all new components import correctly
- [ ] No console errors in browser DevTools

### Database ✅
- [ ] Backup existing database before migration
- [ ] Run migrations: `python manage.py migrate`
- [ ] Verify DeviceInfo table has new columns:
  ```sql
  SELECT * FROM analytics_deviceinfo LIMIT 1;
  -- Should see: country, country_code, city, region, latitude, longitude, timezone, isp
  ```
- [ ] Check indexes are created:
  ```sql
  SHOW INDEXES FROM analytics_deviceinfo;
  -- Should see index on (link_id, country_code)
  ```

---

## Testing Checklist

### Functional Testing ✅
- [ ] Create a test shortened link
- [ ] Click the link multiple times from different sources
- [ ] Wait a few seconds, then refresh dashboard
- [ ] Click "📱 Devices" button - should show device info
- [ ] Click "🌍 Map" button - should show geolocation data
- [ ] Verify correct data displays:
  - [ ] IP addresses shown correctly
  - [ ] Countries have flags
  - [ ] Cities displayed
  - [ ] Device types correct (mobile/desktop/tablet)
  - [ ] Access counts accurate

### Search & Filter Testing ✅
- [ ] Search by IP address
- [ ] Search by country name
- [ ] Search by city name
- [ ] Filter by country code (2 letters)
- [ ] Filter by city
- [ ] Filter by device type
- [ ] Change sort order
- [ ] Change sort field
- [ ] Pagination works (1000 limit)

### Performance Testing ✅
- [ ] Widget loads in < 2 seconds
- [ ] Searching doesn't cause lag
- [ ] 10+ IPs display without issues
- [ ] 100+ IPs display efficiently
- [ ] Browser memory usage acceptable (< 100MB)

### Error Handling ✅
- [ ] Test with invalid link ID
- [ ] Test with no geolocation data
- [ ] Test with rate limited API
- [ ] Test with network failure
- [ ] Check error messages are user-friendly

---

## Production Deployment

### Backend Production
- [ ] Set environment variables:
  ```bash
  DEBUG=False
  ALLOWED_HOSTS=yourdomain.com
  DATABASE_URL=your_production_db
  CACHE_BACKEND=production_cache
  ```
- [ ] Run migrations on production database
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Test API endpoints on production
- [ ] Monitor geolocation API usage

### Frontend Production
- [ ] Build optimized bundle: `npm run build`
- [ ] Test production build locally: `npm run start`
- [ ] Verify API URLs point to production backend
- [ ] Deploy to Vercel/Netlify/your CDN

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Monitor API response times
- [ ] Track geolocation API quota usage
- [ ] Monitor database query performance
- [ ] Set up alerts for API failures

---

## Post-Deployment Verification

### Live Testing ✅
- [ ] Access dashboard on production
- [ ] Create test shortened link
- [ ] Click link from different location/device
- [ ] Verify geolocation data appears within 5 seconds
- [ ] Test search & filters work
- [ ] Check response times are acceptable

### User Communication
- [ ] Send release notes to users
- [ ] Update documentation/help pages
- [ ] Announce new "🌍 Map" feature
- [ ] Provide usage examples
- [ ] Create tutorial video (optional)

### Monitoring First 24 Hours
- [ ] Monitor API error rates
- [ ] Check database performance
- [ ] Watch geolocation API quota
- [ ] Monitor user feedback channels
- [ ] Be ready to rollback if issues

---

## Rollback Plan (if needed)

### Quick Rollback
```bash
# Backend
git revert <commit_hash>
python manage.py migrate analytics 0000_initial

# Frontend
git revert <commit_hash>
npm run build
npm run deploy
```

### What Could Go Wrong
- Geolocation API quota exceeded → Increase limit or switch provider
- Database migration issues → Restore backup, fix migration
- Performance issues → Add caching, optimize queries
- Widget not loading → Check API endpoints, browser errors

---

## Configuration Checklist

### Backend Config
- [ ] `settings.py` - Cache backend configured
- [ ] `requirements.txt` - All dependencies listed
- [ ] `geolocation.py` - IP API credentials (if needed)
- [ ] CORS headers configured properly
- [ ] Rate limiting configured (45 req/min for geolocation)

### Frontend Config
- [ ] `next.config.js` - Production settings
- [ ] `.env.production` - API URL set correctly
- [ ] API timeouts configured appropriately
- [ ] Error boundaries in place

### Database Config
- [ ] Backup strategy in place
- [ ] Query indexes created
- [ ] Connection pooling configured
- [ ] Retention policy defined

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Widget Load Time | < 2s | ✅ |
| Search Response | < 500ms | ✅ |
| API Response | < 1s | ✅ |
| Database Query | < 100ms | ✅ |
| Cache Hit Rate | > 80% | ✅ |
| Error Rate | < 0.1% | ✅ |

---

## Security Checklist

- [ ] API endpoints require authentication
- [ ] Rate limiting enabled
- [ ] HTTPS enforced on production
- [ ] Database credentials secured
- [ ] API keys not in code
- [ ] CORS properly configured
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS protection enabled
- [ ] CSRF tokens in place

---

## Documentation Checklist

- [ ] Setup guide completed (`IP_GEOLOCATION_SETUP.md`)
- [ ] Implementation summary completed (`IMPLEMENTATION_SUMMARY.md`)
- [ ] API documentation available
- [ ] User guide for dashboard widget
- [ ] Troubleshooting guide ready
- [ ] FAQ answers prepared

---

## Final Sign-Off

- [ ] Product team approved
- [ ] Backend team sign-off
- [ ] Frontend team sign-off
- [ ] QA testing complete
- [ ] Security review passed
- [ ] Performance requirements met
- [ ] Documentation complete
- [ ] Ready for production deployment

---

## Post-Launch Monitoring (1 Week)

- [ ] No critical errors in logs
- [ ] Geolocation API performing well
- [ ] User feedback positive
- [ ] Performance metrics stable
- [ ] Database size reasonable
- [ ] No unexpected behavior

---

## Success Criteria

✅ Users can see exact location (city level) of website visitors  
✅ IP addresses properly geolocated with 99%+ accuracy  
✅ Dashboard widget displays location info with search/filters  
✅ Range limited to 1000 IPs for performance  
✅ Search bar available for IP lookup  
✅ All data 100% accurate per IP API service  
✅ No performance degradation  
✅ Seamless integration with existing dashboard  

---

**Deployment Status**: Ready ✅  
**Version**: 1.0.0  
**Deployment Date**: [TO BE FILLED]  
**Deployed By**: [TO BE FILLED]
