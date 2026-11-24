import { Component, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { GithubService, GithubUserResponse } from './github.service';


@Component({
    selector: 'app-root',
    standalone: false,
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    githubUsername = '';
    data = signal<GithubUserResponse | null>(null);
    error = signal('');
    loading = signal(false);

    constructor(private githubService: GithubService) {}

    search() {
        const username = this.githubUsername.trim();
        if (!username) {
            this.error.set('Please enter a GitHub username.');
            this.data.set(null);
            return;
        }

        this.loading.set(true);
        this.error.set('');
        this.data.set(null);

        this.githubService.getUser(username)
            .pipe(finalize(() => this.loading.set(false)))
            .subscribe({
                next: (data) => this.data.set(data),
                error: (err: HttpErrorResponse) => {
                    if (err.status === 0) {
                        this.error.set('Could not reach the backend. Is it running on http://127.0.0.1:8000?');
                    } else {
                        this.error.set(err.error?.detail || 'Something went wrong. Please try again.');
                    }
                }
            });
    }

}
